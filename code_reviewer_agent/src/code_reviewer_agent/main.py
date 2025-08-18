#!/usr/bin/env python
import os
from pathlib import Path
from code_reviewer_agent.crew import CodeReviewerAgentCrew

def run():
    """
    Run the simplified code reviewer agent.
    """
    target_path = "/Users/gk/Documents/GitHub/recognition"
    
    if not Path(target_path).exists():
        print(f"Error: Path '{target_path}' does not exist.")
        return
    
    os.makedirs('output', exist_ok=True)
    
    inputs = {
        'path': target_path
    }
    
    print(f"🔍 Starting simplified code review for: {target_path}")
    print("📋 Generating 3 focused reports:")
    print("  1. Error & Suggestions Report")
    print("  2. Security Report") 
    print("  3. Performance Report")
    print("=" * 50)
    
    try:
        crew_instance = CodeReviewerAgentCrew()
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        print("\n" + "=" * 50)
        print("✅ Code review completed successfully!")
        print("\n📊 Reports generated:")
        print("- output/error_suggestions_report.md")
        print("- output/security_report.md")
        print("- output/performance_report.md")
        
        # Quick summary
        print(f"\n📋 Summary:")
        print("✅ Error analysis completed")
        print("✅ Security scan completed")
        print("✅ Performance analysis completed")
        
    except Exception as e:
        print(f"❌ Error during code review: {str(e)}")
        print("💡 Try running again in a few minutes if rate limited.")

if __name__ == "__main__":
    run()