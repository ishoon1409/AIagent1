import boto3
import json
import re
import os
from import_resolver import resolve_import_conflicts, extract_imports

class AIConflictResolver:
    def __init__(self, model_id='anthropic.claude-v2'):
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name='us-west-2'  # Change to your region
        )
        self.model_id = model_id
    
    def detect_conflict_type(self, content, file_path):
        """Detect the type of conflict."""
        if file_path.endswith('.py') and self._is_import_conflict(content):
            return "import"
        return "other"
    
    def _is_import_conflict(self, content):
        """Check if this is likely an import order conflict."""
        # Look for conflict markers near import statements
        conflict_pattern = re.compile(
            r'<<<<<<< .*?\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n',
            re.DOTALL
        )
        
        for match in conflict_pattern.finditer(content):
            head_content = match.group(1)
            feature_content = match.group(2)
            
            head_has_imports = 'import ' in head_content or 'from ' in head_content
            feature_has_imports = 'import ' in feature_content or 'from ' in feature_content
            
            if head_has_imports and feature_has_imports:
                # Check if imports are the only difference
                head_imports = set(extract_imports(head_content))
                feature_imports = set(extract_imports(feature_content))
                
                if head_imports != feature_imports:
                    return True
        
        return False
    
    def resolve_file(self, file_path):
        """Resolve conflicts in the given file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '<<<<<<< ' not in content:
                print(f"No conflicts found in {file_path}")
                return False
            
            conflict_type = self.detect_conflict_type(content, file_path)
            
            if conflict_type == "import":
                # Use our specialized import resolver
                resolved_content = resolve_import_conflicts(content)
                print(f"Resolved import order conflicts in {file_path}")
            else:
                # Use AI for other conflict types
                resolved_content = self._resolve_with_ai(content, file_path)
                print(f"Used AI to resolve conflicts in {file_path}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(resolved_content)
            
            return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return False
    
    def _resolve_with_ai(self, content, file_path):
        """Use AWS Bedrock to resolve conflicts."""
        file_ext = os.path.splitext(file_path)[1]
        
        # Extract all conflicts
        conflict_pattern = re.compile(
            r'<<<<<<< .*?\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n',
            re.DOTALL
        )
        
        def resolve_conflict(match):
            head_content = match.group(1)
            feature_content = match.group(2)
            
            # Prepare the prompt for AI
            prompt = f"""
            I need to resolve a Git merge conflict in a {file_ext} file. Please analyze both versions and provide the resolved code.
            
            VERSION A (HEAD):
            ```
            {head_content}
            ```
            
            VERSION B (incoming):
            ```
            {feature_content}
            ```
            
            In your answer, provide ONLY the resolved code without any explanations or formatting. Do not include conflict markers or version headers.
            """
            
            # Call AWS Bedrock API
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens_to_sample": 4000,
                    "temperature": 0.2,
                    "top_p": 0.9,
                })
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            resolved = response_body['completion'].strip()
            
            # Clean up any markdown code blocks the model might have added
            resolved = resolved.replace('```python', '').replace('```', '').strip()
            
            return resolved
        
        # Replace each conflict with the AI-resolved version
        resolved_content = conflict_pattern.sub(resolve_conflict, content)
        return resolved_content