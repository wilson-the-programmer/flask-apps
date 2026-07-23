

from flask import Flask, request, render_template_string
import subprocess
import sys
import io
import tempfile
import os
from markupsafe import escape

app = Flask(__name__)

HTML = r"""
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Code Runner</title>

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/codemirror@5/lib/codemirror.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/codemirror@5/theme/neo.min.css">

    <style>
        body {
            background-color: black;
            color: grey;
            font-family: monospace;
            padding: 10px;
            margin: 0;
        }

        .CodeMirror {
            height: 840px;
            width: 98%;
            font-size: 40px;
            font-weight: bold;
            text-shadow: 0 0 1px black;
            line-height: 1.4;
            padding: 12px;
            font-family: monospace;
            border: 6px outset #222;
            box-sizing: border-box;
        }

        #output {
            width: 100%;
            height: 32em;
            font-size: 42px;
            font-weight: bold;
            text-shadow: 0 0 2px black;
            font-family: monospace;
            background-color: white;
            color: black;
            border: 12px solid grey;
            overflow-x: auto;
            white-space: pre-wrap;
            margin-top: 10px;
            padding: 12px;
            box-sizing: border-box;
        }

        .button-row {
            display: flex;
            gap: 12px;
            margin-bottom: 10px;
        }

        button.code-btn {
            font-family: monospace, "Courier New";
            font-weight: bold;
            font-size: 36px;
            padding: 15px 0;
            background-color: #222222;
            color: white;
            border: 8px outset white;
            cursor: pointer;
            flex: 1;
            min-width: 0;
            height: 120px;
        }
    </style>
</head>
<body>
    <form method="POST" id="code-form">
        <input type="hidden" name="mode" id="mode" value="">
        <textarea id="code" name="code" spellcheck="false">{{ code }}</textarea><br>

        <div class="button-row">
            <button class="code-btn" type="button" onclick="run('c')">C &gt;</button>
            <button class="code-btn" type="button" onclick="run('cpp')">C++ &gt;</button>
            <button class="code-btn" type="button" onclick="run('rust')">Rust &gt;</button>
            <button class="code-btn" type="button" onclick="run('golang')">Golang &gt;</button>
        </div>

        <div class="button-row">
            <button class="code-btn" type="button" onclick="run('bash')">Bash &gt;</button>
            <button class="code-btn" type="button" onclick="run('python')">Python &gt;</button>
            <button class="code-btn" type="button" onclick="run('javascript')">JS &gt;</button>
            <button class="code-btn" type="button" onclick="saveFile()">Save</button>
        </div>

        <textarea id="output" readonly>{{ output }}</textarea>
    </form>

    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/lib/codemirror.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/mode/python/python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/mode/javascript/javascript.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/mode/shell/shell.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/mode/clike/clike.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/mode/go/go.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/addon/edit/closebrackets.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/codemirror@5/addon/edit/matchbrackets.min.js"></script>

    <script>
        const editor = CodeMirror.fromTextArea(document.getElementById("code"), {
            lineNumbers: true,
            theme: "neo",
            mode: "python",
            indentUnit: 4,
            tabSize: 4,
            indentWithTabs: false,
            autoCloseBrackets: true,
            matchBrackets: true
        });

        function run(mode) {
            document.getElementById("mode").value = mode;
            document.getElementById("code").value = editor.getValue();
            document.getElementById("code-form").submit();
        }

        function saveFile() {
            const code = editor.getValue();
            const blob = new Blob([code], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = "code.txt";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    output = ""

    if request.method == "POST":
        code = request.form.get("code", "")
        mode = request.form.get("mode", "")

        try:
            if mode == "python":
                old_stdout = sys.stdout
                redirected_output = sys.stdout = io.StringIO()
                exec(code, {})
                output = redirected_output.getvalue()
                sys.stdout = old_stdout

            elif mode == "javascript":
                output = subprocess.check_output(
                    ["node", "-e", code], stderr=subprocess.STDOUT
                ).decode()

            elif mode == "golang":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".go") as tmp:
                    tmp.write(code.encode())
                    tmp_path = tmp.name
                try:
                    output = subprocess.check_output(
                        ["go", "run", tmp_path], stderr=subprocess.STDOUT
                    ).decode()
                finally:
                    os.remove(tmp_path)

            elif mode == "bash":
                code = code.replace("\n", "").replace("\r", "")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".sh", mode="w") as f:
                    f.write(code)
                    path = f.name
                try:
                    output = subprocess.check_output(
                        ["bash", path], stderr=subprocess.STDOUT
                    ).decode()
                except subprocess.CalledProcessError as e:
                    output = e.output.decode()
                finally:
                    os.remove(path)

            elif mode == "c":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
                    tmp.write(code.encode())
                    tmp_path = tmp.name
                exe_path = tmp_path + ".out"
                try:
                    subprocess.check_output(
                        ["gcc", tmp_path, "-o", exe_path], stderr=subprocess.STDOUT
                    )
                    output = subprocess.check_output(
                        [exe_path], stderr=subprocess.STDOUT
                    ).decode()
                finally:
                    os.remove(tmp_path)
                    if os.path.exists(exe_path):
                        os.remove(exe_path)

            elif mode == "cpp":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as tmp:
                    tmp.write(code.encode())
                    tmp_path = tmp.name
                exe_path = tmp_path + ".out"
                try:
                    subprocess.check_output(
                        ["g++", tmp_path, "-o", exe_path], stderr=subprocess.STDOUT
                    )
                    output = subprocess.check_output(
                        [exe_path], stderr=subprocess.STDOUT
                    ).decode()
                finally:
                    os.remove(tmp_path)
                    if os.path.exists(exe_path):
                        os.remove(exe_path)

            elif mode == "rust":
                with tempfile.TemporaryDirectory() as tmpdir:
                    rs_file = os.path.join(tmpdir, "main.rs")
                    exe_file = os.path.join(tmpdir, "main_exe")
                    with open(rs_file, "w") as f:
                        f.write(code)
                    subprocess.check_output(
                        ["rustc", rs_file, "-o", exe_file], stderr=subprocess.STDOUT
                    )
                    output = subprocess.check_output(
                        [exe_file], stderr=subprocess.STDOUT
                    ).decode()

            elif mode.lower() == "html":
                output = code

        except subprocess.CalledProcessError as e:
            output = f"{mode.capitalize()} Error: {e.output.decode()}"
        except Exception as e:
            output = f"{mode.capitalize()} Error: {e}"

    return render_template_string(
        HTML,
        code=escape(code),
        output=escape(output)
    )

if __name__ == "__main__":
    app.run(port=8600)
