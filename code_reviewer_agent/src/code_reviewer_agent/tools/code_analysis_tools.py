import os
import ast
import re
import subprocess
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class CodeParserInput(BaseModel):
    """Input for code parser tool."""
    path: str = Field(..., description="Path to file or directory to analyze")

class CodeParserTool(BaseTool):
    name: str = "Code Parser Tool"
    description: str = "Parses files or directories to identify code files for analysis"
    args_schema: type[BaseModel] = CodeParserInput

    def _run(self, path: str) -> str:
        """Parse the given path and return code files information."""
        supported_extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.cs': 'csharp'
        }
        
        files_info = []
        path_obj = Path(path)
        
        if path_obj.is_file():
            files_to_analyze = [path_obj]
        elif path_obj.is_dir():
            files_to_analyze = []
            for ext in supported_extensions.keys():
                files_to_analyze.extend(path_obj.rglob(f"*{ext}"))
        else:
            return f"Error: Path '{path}' does not exist."
        
        for file_path in files_to_analyze:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                extension = file_path.suffix.lower()
                language = supported_extensions.get(extension, 'unknown')
                
                lines_of_code = len([line for line in content.split('\n') if line.strip()])
                
                files_info.append({
                    'path': str(file_path),
                    'language': language,
                    'size_bytes': file_path.stat().st_size,
                    'lines_of_code': lines_of_code,
                    'content': content[:5000] + "..." if len(content) > 5000 else content  # Truncate for large files
                })
                
            except Exception as e:
                files_info.append({
                    'path': str(file_path),
                    'error': f"Could not read file: {str(e)}"
                })
        
        return self._format_files_info(files_info)
    
    def _format_files_info(self, files_info: List[Dict]) -> str:
        if not files_info:
            return "No supported code files found."
        
        report = "# Code Files Inventory\n\n"
        report += f"**Total files found:** {len(files_info)}\n\n"
        
        # Group by language
        by_language = {}
        for file_info in files_info:
            if 'error' not in file_info:
                lang = file_info['language']
                if lang not in by_language:
                    by_language[lang] = []
                by_language[lang].append(file_info)
        
        report += "## Files by Language\n\n"
        for language, files in by_language.items():
            report += f"### {language.title()}\n"
            total_lines = sum(f['lines_of_code'] for f in files)
            report += f"- **Files:** {len(files)}\n"
            report += f"- **Total Lines:** {total_lines}\n\n"
            
            for file_info in files:
                report += f"**{file_info['path']}**\n"
                report += f"- Size: {file_info['size_bytes']} bytes\n"
                report += f"- Lines: {file_info['lines_of_code']}\n\n"
        
        return report

class StaticAnalysisInput(BaseModel):
    """Input for static analysis tool."""
    file_path: str = Field(..., description="Path to the file to analyze")
    language: str = Field(..., description="Programming language of the file")
    content: str = Field(..., description="File content to analyze")

class StaticAnalysisTool(BaseTool):
    name: str = "Static Analysis Tool"
    description: str = "Performs static code analysis using various tools and techniques"
    args_schema: type[BaseModel] = StaticAnalysisInput

    def _run(self, file_path: str, language: str, content: str) -> str:
        """Perform static analysis on the given file."""
        issues = []
        
        if language == 'python':
            issues.extend(self._analyze_python(file_path, content))
        elif language == 'javascript':
            issues.extend(self._analyze_javascript(file_path, content))
        # Add more languages as needed
        
        # Generic analysis for all languages
        issues.extend(self._generic_analysis(file_path, content))
        
        return self._format_static_analysis_report(file_path, issues)
    
    def _analyze_python(self, file_path: str, content: str) -> List[Dict]:
        """Analyze Python code."""
        issues = []
        
        try:
            # AST-based analysis
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check for bare except clauses
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append({
                        'line': node.lineno,
                        'type': 'Code Quality',
                        'severity': 'Medium',
                        'message': 'Bare except clause catches all exceptions',
                        'suggestion': 'Catch specific exception types instead of using bare except'
                    })
                
                # Check for eval/exec usage
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append({
                            'line': node.lineno,
                            'type': 'Security',
                            'severity': 'High',
                            'message': f'Use of {node.func.id}() is dangerous',
                            'suggestion': 'Avoid eval/exec or use safer alternatives'
                        })
        
        except SyntaxError as e:
            issues.append({
                'line': e.lineno or 0,
                'type': 'Syntax Error',
                'severity': 'Critical',
                'message': f'Syntax error: {e.msg}',
                'suggestion': 'Fix the syntax error'
            })
        
        # Try to run pylint if available
        try:
            result = subprocess.run(
                ['pylint', '--output-format=json', file_path],
                capture_output=True, text=True, timeout=30
            )
            if result.stdout:
                pylint_issues = json.loads(result.stdout)
                for issue in pylint_issues:
                    issues.append({
                        'line': issue.get('line', 0),
                        'type': issue.get('type', 'Unknown'),
                        'severity': self._map_pylint_severity(issue.get('type', '')),
                        'message': issue.get('message', ''),
                        'suggestion': f"Pylint {issue.get('symbol', '')}: {issue.get('message', '')}"
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass  # Pylint not available or failed
        
        return issues
    
    def _analyze_javascript(self, file_path: str, content: str) -> List[Dict]:
        """Analyze JavaScript code."""
        issues = []
        
        # Basic pattern matching for common issues
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for console.log (should be removed in production)
            if 'console.log' in line:
                issues.append({
                    'line': i,
                    'type': 'Code Quality',
                    'severity': 'Low',
                    'message': 'console.log statement found',
                    'suggestion': 'Remove console.log statements in production code'
                })
            
            # Check for == instead of ===
            if re.search(r'[^=!]==[^=]', line):
                issues.append({
                    'line': i,
                    'type': 'Code Quality',
                    'severity': 'Medium',
                    'message': 'Use of == instead of ===',
                    'suggestion': 'Use strict equality (===) instead of loose equality (==)'
                })
        
        return issues
    
    def _generic_analysis(self, file_path: str, content: str) -> List[Dict]:
        """Generic analysis applicable to all languages."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'type': 'Style',
                    'severity': 'Low',
                    'message': f'Line too long ({len(line)} characters)',
                    'suggestion': 'Break long lines for better readability'
                })
            
            # Check for TODO/FIXME comments
            if re.search(r'(TODO|FIXME|HACK)', line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'type': 'Code Quality',
                    'severity': 'Low',
                    'message': 'Unresolved TODO/FIXME comment',
                    'suggestion': 'Address the TODO/FIXME or remove if no longer needed'
                })
        
        return issues
    
    def _map_pylint_severity(self, pylint_type: str) -> str:
        """Map pylint message types to severity levels."""
        mapping = {
            'error': 'Critical',
            'warning': 'Medium',
            'refactor': 'Low',
            'convention': 'Low',
            'info': 'Low'
        }
        return mapping.get(pylint_type.lower(), 'Medium')
    
    def _format_static_analysis_report(self, file_path: str, issues: List[Dict]) -> str:
        """Format the static analysis report."""
        if not issues:
            return f"## Static Analysis: {file_path}\n\nNo issues found! ✅"
        
        report = f"## Static Analysis: {file_path}\n\n"
        report += f"**Total issues found:** {len(issues)}\n\n"
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue['severity']
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
        
        for severity in ['Critical', 'High', 'Medium', 'Low']:
            if severity in by_severity:
                report += f"### {severity} Issues ({len(by_severity[severity])})\n\n"
                for issue in by_severity[severity]:
                    report += f"**Line {issue['line']}** - {issue['type']}\n"
                    report += f"- **Issue:** {issue['message']}\n"
                    report += f"- **Suggestion:** {issue['suggestion']}\n\n"
        
        return report

class SecurityAnalyzerInput(BaseModel):
    """Input for security analyzer tool."""
    file_path: str = Field(..., description="Path to the file to analyze")
    language: str = Field(..., description="Programming language")
    content: str = Field(..., description="File content")

class SecurityAnalyzerTool(BaseTool):
    name: str = "Security Analyzer Tool"
    description: str = "Analyzes code for security vulnerabilities and unsafe patterns"
    args_schema: type[BaseModel] = SecurityAnalyzerInput

    def _run(self, file_path: str, language: str, content: str) -> str:
        """Perform security analysis."""
        vulnerabilities = []
        
        # Common security patterns across languages
        security_patterns = {
            'Hardcoded Secrets': [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                r'secret\s*=\s*["\'][^"\']{10,}["\']',
                r'token\s*=\s*["\'][^"\']{20,}["\']'
            ],
            'SQL Injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'SELECT.*\+.*FROM',
                r'INSERT.*\+.*VALUES'
            ],
            'Command Injection': [
                r'os\.system\s*\(',
                r'subprocess\.(call|run|Popen).*shell\s*=\s*True',
                r'exec\s*\(',
                r'eval\s*\('
            ],
            'Path Traversal': [
                r'open\s*\(\s*.*\.\./.*\)',
                r'file\s*\(\s*.*\.\./.*\)',
                r'include\s*\(\s*.*\.\./.*\)'
            ]
        }
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for vuln_type, patterns in security_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append({
                            'line': i,
                            'type': vuln_type,
                            'severity': self._get_vulnerability_severity(vuln_type),
                            'code': line.strip(),
                            'description': self._get_vulnerability_description(vuln_type),
                            'recommendation': self._get_security_recommendation(vuln_type)
                        })
        
        # Language-specific security checks
        if language == 'python':
            vulnerabilities.extend(self._python_security_checks(content))
        elif language == 'javascript':
            vulnerabilities.extend(self._javascript_security_checks(content))
        
        return self._format_security_report(file_path, vulnerabilities)
    
    def _python_security_checks(self, content: str) -> List[Dict]:
        """Python-specific security checks."""
        issues = []
        
        # Check for pickle usage (can be dangerous)
        if 'pickle.load' in content or 'pickle.loads' in content:
            issues.append({
                'line': 0,
                'type': 'Deserialization',
                'severity': 'High',
                'code': 'pickle.load/loads usage detected',
                'description': 'Pickle deserialization can execute arbitrary code',
                'recommendation': 'Use safer serialization formats like JSON'
            })
        
        return issues
    
    def _javascript_security_checks(self, content: str) -> List[Dict]:
        """JavaScript-specific security checks."""
        issues = []
        
        # Check for innerHTML usage (XSS risk)
        if 'innerHTML' in content:
            issues.append({
                'line': 0,
                'type': 'XSS',
                'severity': 'Medium',
                'code': 'innerHTML usage detected',
                'description': 'innerHTML can lead to XSS vulnerabilities',
                'recommendation': 'Use textContent or properly sanitize input'
            })
        
        return issues
    
    def _get_vulnerability_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        severity_map = {
            'SQL Injection': 'Critical',
            'Command Injection': 'Critical',
            'Hardcoded Secrets': 'High',
            'Path Traversal': 'High',
            'XSS': 'Medium',
            'Deserialization': 'High'
        }
        return severity_map.get(vuln_type, 'Medium')
    
    def _get_vulnerability_description(self, vuln_type: str) -> str:
        """Get description for vulnerability type."""
        descriptions = {
            'SQL Injection': 'Potential SQL injection vulnerability detected',
            'Command Injection': 'Command injection vulnerability detected',
            'Hardcoded Secrets': 'Hardcoded credentials or secrets found',
            'Path Traversal': 'Path traversal vulnerability detected',
            'XSS': 'Cross-site scripting vulnerability detected',
            'Deserialization': 'Unsafe deserialization detected'
        }
        return descriptions.get(vuln_type, 'Security issue detected')
    
    def _get_security_recommendation(self, vuln_type: str) -> str:
        """Get recommendation for vulnerability type."""
        recommendations = {
            'SQL Injection': 'Use parameterized queries or prepared statements',
            'Command Injection': 'Avoid executing user input as commands, use safer alternatives',
            'Hardcoded Secrets': 'Use environment variables or secure key management systems',
            'Path Traversal': 'Validate and sanitize file paths, use allowlists',
            'XSS': 'Sanitize user input and use proper encoding',
            'Deserialization': 'Use safer serialization formats or validate input'
        }
        return recommendations.get(vuln_type, 'Review code for security implications')
    
    def _format_security_report(self, file_path: str, vulnerabilities: List[Dict]) -> str:
        """Format security analysis report."""
        if not vulnerabilities:
            return f"## Security Analysis: {file_path}\n\nNo security issues detected! ✅"
        
        report = f"## Security Analysis: {file_path}\n\n"
        report += f"**Total vulnerabilities found:** {len(vulnerabilities)}\n\n"
        
        # Group by severity
        by_severity = {}
        for vuln in vulnerabilities:
            severity = vuln['severity']
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(vuln)
        
        for severity in ['Critical', 'High', 'Medium', 'Low']:
            if severity in by_severity:
                report += f"### {severity} Vulnerabilities ({len(by_severity[severity])})\n\n"
                for vuln in by_severity[severity]:
                    report += f"**{vuln['type']}** (Line {vuln['line']})\n"
                    report += f"- **Description:** {vuln['description']}\n"
                    report += f"- **Code:** `{vuln['code']}`\n"
                    report += f"- **Recommendation:** {vuln['recommendation']}\n\n"
        
        return report

class PerformanceAnalyzerInput(BaseModel):
    """Input for performance analyzer tool."""
    file_path: str = Field(..., description="Path to the file to analyze")
    language: str = Field(..., description="Programming language")
    content: str = Field(..., description="File content")

class PerformanceAnalyzerTool(BaseTool):
    name: str = "Performance Analyzer Tool"
    description: str = "Analyzes code for performance issues and optimization opportunities"
    args_schema: type[BaseModel] = PerformanceAnalyzerInput

    def _run(self, file_path: str, language: str, content: str) -> str:
        """Perform performance analysis."""
        performance_issues = []
        
        if language == 'python':
            performance_issues.extend(self._analyze_python_performance(content))
        elif language == 'javascript':
            performance_issues.extend(self._analyze_javascript_performance(content))
        
        # Generic performance analysis
        performance_issues.extend(self._generic_performance_analysis(content))
        
        return self._format_performance_report(file_path, performance_issues)
    
    def _analyze_python_performance(self, content: str) -> List[Dict]:
        """Analyze Python code for performance issues."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for inefficient string concatenation
            if '+=' in line and 'str' in line.lower():
                issues.append({
                    'line': i,
                    'type': 'String Concatenation',
                    'severity': 'Medium',
                    'issue': 'Inefficient string concatenation in loop',
                    'suggestion': 'Use join() or f-strings for better performance',
                    'code': line.strip()
                })
            
            # Check for list comprehension opportunities
            if 'for ' in line and 'append(' in line:
                issues.append({
                    'line': i,
                    'type': 'List Operations',
                    'severity': 'Low',
                    'issue': 'Could use list comprehension',
                    'suggestion': 'Consider using list comprehension for better performance',
                    'code': line.strip()
                })
        
        return issues
    
    def _analyze_javascript_performance(self, content: str) -> List[Dict]:
        """Analyze JavaScript code for performance issues."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for inefficient DOM queries
            if 'document.getElementById' in line and 'for' in line:
                issues.append({
                    'line': i,
                    'type': 'DOM Operations',
                    'severity': 'Medium',
                    'issue': 'DOM query inside loop',
                    'suggestion': 'Cache DOM elements outside loops',
                    'code': line.strip()
                })
        
        return issues
    
    def _generic_performance_analysis(self, content: str) -> List[Dict]:
        """Generic performance analysis."""
        issues = []
        lines = content.split('\n')
        
        # Check for nested loops (potential O(n²) complexity)
        nested_loop_depth = 0
        for i, line in enumerate(lines, 1):
            if re.search(r'\bfor\b|\bwhile\b', line):
                nested_loop_depth += 1
                if nested_loop_depth > 2:
                    issues.append({
                        'line': i,
                        'type': 'Algorithmic Complexity',
                        'severity': 'High',
                        'issue': 'Deeply nested loops detected',
                        'suggestion': 'Consider optimizing algorithm to reduce complexity',
                        'code': line.strip()
                    })
            elif line.strip() == '' or not line.strip().startswith(' '):
                nested_loop_depth = 0
        
        return issues
    
    def _format_performance_report(self, file_path: str, issues: List[Dict]) -> str:
        """Format performance analysis report."""
        if not issues:
            return f"## Performance Analysis: {file_path}\n\nNo performance issues detected! ✅"
        
        report = f"## Performance Analysis: {file_path}\n\n"
        report += f"**Total performance issues found:** {len(issues)}\n\n"
        
        # Group by type
        by_type = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        for issue_type, type_issues in by_type.items():
            report += f"### {issue_type} ({len(type_issues)} issues)\n\n"
            for issue in type_issues:
                report += f"**Line {issue['line']}** - {issue['severity']} Priority\n"
                report += f"- **Issue:** {issue['issue']}\n"
                report += f"- **Code:** `{issue['code']}`\n"
                report += f"- **Suggestion:** {issue['suggestion']}\n\n"
        
        return report

class ComplexityAnalyzerInput(BaseModel):
    """Input for complexity analyzer tool."""
    file_path: str = Field(..., description="Path to the file to analyze")
    content: str = Field(..., description="File content")

class ComplexityAnalyzerTool(BaseTool):
    name: str = "Complexity Analyzer Tool"
    description: str = "Analyzes code complexity metrics"
    args_schema: type[BaseModel] = ComplexityAnalyzerInput

    def _run(self, file_path: str, content: str) -> str:
        """Analyze code complexity."""
        try:
            # Try to use radon for Python files
            if file_path.endswith('.py'):
                result = subprocess.run(
                    ['radon', 'cc', file_path, '-j'],
                    capture_output=True, text=True, timeout=30
                )
                if result.stdout:
                    complexity_data = json.loads(result.stdout)
                    return self._format_complexity_report(file_path, complexity_data)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Fallback to basic complexity analysis
        return self._basic_complexity_analysis(file_path, content)
    
    def _basic_complexity_analysis(self, file_path: str, content: str) -> str:
        """Basic complexity analysis when tools aren't available."""
        lines = content.split('\n')
        
        # Count decision points
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'case', 'switch']
        complexity_score = 1  # Base complexity
        
        for line in lines:
            for keyword in decision_keywords:
                if f' {keyword} ' in line or line.strip().startswith(keyword):
                    complexity_score += 1
        
        report = f"## Complexity Analysis: {file_path}\n\n"
        report += f"**Estimated Cyclomatic Complexity:** {complexity_score}\n\n"
        
        if complexity_score > 10:
            report += "⚠️ **High Complexity Warning**\n"
            report += "This file has high complexity. Consider refactoring into smaller functions.\n\n"
        elif complexity_score > 5:
            report += "⚡ **Moderate Complexity**\n"
            report += "This file has moderate complexity. Monitor for further growth.\n\n"
        else:
            report += "✅ **Low Complexity**\n"
            report += "This file has acceptable complexity.\n\n"
        
        return report
    
    def _format_complexity_report(self, file_path: str, complexity_data: Dict) -> str:
        """Format complexity report from radon output."""
        report = f"## Complexity Analysis: {file_path}\n\n"
        
        if file_path in complexity_data:
            functions = complexity_data[file_path]
            if functions:
                report += "### Function Complexity\n\n"
                for func in functions:
                    report += f"**{func['name']}** (Line {func['lineno']})\n"
                    report += f"- Complexity: {func['complexity']}\n"
                    report += f"- Grade: {func['rank']}\n\n"
        
        return report