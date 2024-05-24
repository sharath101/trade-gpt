from baseclasses import Strategy
import ast


class StrategyImporter:
    def __init__(self):
        pass

    def parse(self, code):
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
            def visit_Import(self, node):
                suspicious.append(f"Suspicious import statement: {ast.dump(node)}")
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
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

        analyzer = CodeAnalyzer()
        analyzer.visit(tree)

        return errors, suspicious
