from baseclasses import Strategy
import ast


class StrategyImporter:
    def __init__(self):
        pass

    def parse(self, code, user_files):
        errors = []
        suspicious = []

        try:
            # Parse the code into an AST
            tree = ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax Error: {e}")
            return errors, suspicious

        # Visitor class to analyze the AST nodes
        class CodeAnalyzer(ast.NodeVisitor):
            def __init__(self, user_files):
                self.user_files = user_files

            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name not in self.user_files and alias.name + ".py" not in self.user_files:
                        suspicious.append(f"Suspicious import statement: {ast.dump(node)}")
                self.generic_visit(node)

            def visit_ImportFrom(self, node):                
                if node.module not in self.user_files and node.module + ".py" not in self.user_files:
                    suspicious.append(f"Suspicious import statement: {ast.dump(node)}")
                self.generic_visit(node)

            def visit_Exec(self, node):
                suspicious.append(f"Suspicious exec statement: {ast.dump(node)}")
                self.generic_visit(node)

            def visit_Eval(self, node):
                suspicious.append(f"Suspicious eval statement: {ast.dump(node)}")
                self.generic_visit(node)

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval", "compile", "open", "input"}:
                    suspicious.append(f"Suspicious function call: {ast.dump(node)}")
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'Strategy':  # Change 'BaseClass' to your base class name
                        suspicious.append(f"Class {node.name} inherits from Strategy")
                self.generic_visit(node)

        analyzer = CodeAnalyzer(user_files)
        analyzer.visit(tree)

        return errors, suspicious
