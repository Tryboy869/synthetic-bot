#!/usr/bin/env python3
"""
Synthetic Python Bot v1.0.0-beta
Self-correcting Python runtime with gravitational compression
"""
import sys, json, traceback, re
from typing import Dict, List, Any

try:
    from gravitational_memory import CompressedMemory
    from auto_training import AutoTrainer
    ADVANCED = True
except: ADVANCED = False

class SyntheticPythonBot:
    def __init__(self, enable_compression=True, enable_auto_training=False, github_token=None, repo_owner=None):
        self.generated_code, self.execution_history, self.learned_fixes = {}, [], {}
        self.compressed_memory = CompressedMemory(15) if enable_compression and ADVANCED else None
        self.auto_trainer = AutoTrainer(github_token, repo_owner) if enable_auto_training and ADVANCED else None
    
    def generate_function(self, name: str, purpose: str) -> str:
        templates = {
            "fibonacci": "def {name}(n: int) -> int:\n    if n <= 1: return n\n    a, b = 0, 1\n    for _ in range(n - 1): a, b = b, a + b\n    return b",
            "factorial": "def {name}(n: int) -> int:\n    if n <= 1: return 1\n    result = 1\n    for i in range(2, n + 1): result *= i\n    return result",
            "sort": "def {name}(arr: list) -> list:\n    if len(arr) <= 1: return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return {name}(left) + middle + {name}(right)"
        }
        for keyword, template in templates.items():
            if keyword in purpose.lower():
                code = template.format(name=name)
                self.generated_code[name] = code
                return code
        code = f"def {name}(*args, **kwargs):\n    \"\"\"Auto-generated: {purpose}\"\"\"\n    pass"
        self.generated_code[name] = code
        return code
    
    def execute_with_autocorrect(self, code: str, max_attempts=3) -> Dict[str, Any]:
        attempt, current_code, corrections = 0, code, []
        while attempt < max_attempts:
            attempt += 1
            try:
                exec(current_code, {})
                result = {"success": True, "attempt": attempt, "code": current_code, "corrections": corrections}
                self.execution_history.append(result)
                return result
            except Exception as e:
                error_type, error_msg = type(e).__name__, str(e)
                corrected, desc = self._auto_correct(current_code, e, traceback.format_exc())
                if corrected == current_code:
                    return {"success": False, "error": error_msg, "type": error_type, "attempts": attempt}
                corrections.append(desc)
                current_code = corrected
                self._learn(error_type, error_msg, desc, attempt < max_attempts)
        return {"success": False, "error": "Max attempts", "attempts": attempt}
    
    def _auto_correct(self, code, error, tb):
        error_type, error_msg = type(error).__name__, str(error)
        if error_type == "NameError" and (m := re.search(r"name '(\w+)' is not defined", error_msg)):
            var = m.group(1)
            val = "0" if any(op in code for op in ['+','-','*']) else "[]" if '[' in code else "{}" if '{' in code else "None"
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if 'def ' in line:
                    next_idx = i + 1
                    while next_idx < len(lines) and ('"""' in lines[next_idx] or not lines[next_idx].strip()): next_idx += 1
                    if next_idx < len(lines):
                        indent = len(lines[next_idx]) - len(lines[next_idx].lstrip())
                        lines.insert(next_idx, " " * indent + f"{var} = {val}\n")
                        return '\n'.join(lines), f"Added {var} = {val}"
        elif error_type == "ZeroDivisionError" and '/' in code:
            protected = re.sub(r'/\s*(\w+)', r'/ (\1 if \1 != 0 else 1)', code)
            if protected != code: return protected, "Protected division"
        elif error_type == "IndexError" and (m := re.search(r'\[(\w+)\]', code)):
            idx = m.group(1)
            protected = code.replace(f'[{idx}]', f'[{idx} if {idx} < len(arr) else 0]')
            if protected != code: return protected, f"Bounds check {idx}"
        elif error_type == "KeyError" and (m := re.search(r"\['(\w+)'\]", code)):
            key = m.group(1)
            protected = code.replace(f"['{key}']", f".get('{key}', None)")
            if protected != code: return protected, f"Safe .get('{key}')"
        return code, "No fix"
    
    def _learn(self, error_type, error_msg, correction, success):
        pattern = f"{error_type}:{error_msg[:50]}"
        if pattern not in self.learned_fixes:
            self.learned_fixes[pattern] = {'count': 1, 'error_type': error_type, 'message': error_msg, 'correction': correction}
        else:
            self.learned_fixes[pattern]['count'] += 1
        if self.compressed_memory: self.compressed_memory.store_pattern(pattern, self.learned_fixes[pattern])
        if self.auto_trainer: self.auto_trainer.learn_correction(error_type, error_msg, correction, success)
    
    def get_stats(self):
        stats = {'generated': len(self.generated_code), 'executions': len(self.execution_history), 'learned': len(self.learned_fixes)}
        if self.compressed_memory:
            cs = self.compressed_memory.get_stats()
            stats['compression'] = {'ratio': cs['compression_ratio'], 'saved': cs['space_saved']}
        return stats
    
    def show_learning_report(self):
        if not self.learned_fixes: return "No patterns learned"
        sorted_errors = sorted(self.learned_fixes.items(), key=lambda x: x[1]['count'], reverse=True)
        report = f"\nLEARNING REPORT\nPatterns: {len(self.learned_fixes)}\n\nTop errors:\n"
        for i, (pattern, data) in enumerate(sorted_errors[:5], 1):
            report += f"{i}. {pattern[:50]}... (count: {data['count']})\n"
        return report

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No function"}))
        sys.exit(1)
    fn, args = sys.argv[1], sys.argv[2:]
    bot = SyntheticPythonBot(enable_compression=ADVANCED)
    if fn == "generate_function":
        if len(args) < 2: print(json.dumps({"error": "Need name, purpose"})); sys.exit(1)
        print(bot.generate_function(args[0], args[1]))
    elif fn == "execute_with_autocorrect":
        if len(args) < 1: print(json.dumps({"error": "Need code"})); sys.exit(1)
        print(json.dumps(bot.execute_with_autocorrect(args[0], int(args[1]) if len(args) > 1 else 3)))
    elif fn == "get_stats":
        print(json.dumps(bot.get_stats()))
    elif fn == "show_learning_report":
        print(bot.show_learning_report())
    else:
        print(json.dumps({"error": f"Unknown: {fn}"}))
        sys.exit(1)

if __name__ == '__main__': main()
