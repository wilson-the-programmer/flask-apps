""" Web IDE """
from flask import Flask, request
import subprocess
import sys
import io
import tempfile
import os

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    output = ""

    if request.method == "POST":
        code = request.form.get("code", "")
        mode = request.form.get("mode", "")

        if mode == "python":
            try:
                old_stdout = sys.stdout
                redirected_output = sys.stdout = io.StringIO()
                exec(code, {})
                output = redirected_output.getvalue()
                sys.stdout = old_stdout
            except Exception as e:
                output = f"Python Error: {e}"

        elif mode == "javascript":
            try:
                result = subprocess.check_output(
                    ["node", "-e", code], stderr=subprocess.STDOUT
                ).decode()
                output = result
            except subprocess.CalledProcessError as e:
                output = "JavaScript Error:\n" + e.output.decode()

        elif mode == "golang":
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".go") as tmp:
                    tmp.write(code.encode())
                    tmp_path = tmp.name

                result = subprocess.check_output(
                    ["go", "run", tmp_path], stderr=subprocess.STDOUT
                ).decode()

                output = result
                os.remove(tmp_path)

            except subprocess.CalledProcessError as e:
                output = "Go Error:\n" + e.output.decode()
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        elif mode == "bash":
            try:
                result = subprocess.check_output(
                    ["bash", "-c", code], stderr=subprocess.STDOUT
                ).decode()
                output = result
            except subprocess.CalledProcessError as e:
                output = "Bash Error:\n" + e.output.decode()



        elif mode == "c":
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
                    tmp.write(code.encode())
                    tmp_path = tmp.name
                    exe_path = tmp_path + ".out"

                subprocess.check_output(
                    ["gcc", tmp_path, "-o", exe_path], stderr=subprocess.STDOUT
                )
                result = subprocess.check_output(
                    [exe_path], stderr=subprocess.STDOUT
                ).decode()
                output = result
                os.remove(tmp_path)
                os.remove(exe_path)

            except subprocess.CalledProcessError as e:
                output = "C Error:\n" + e.output.decode()
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                if os.path.exists(exe_path):
                    os.remove(exe_path)

        elif mode == "rust":
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    rs_file = os.path.join(tmpdir, "main.rs")
                    exe_file = os.path.join(tmpdir, "main_exe")
                    with open(rs_file, "w") as f:
                        f.write(code)
                    subprocess.check_output(
                        ["rustc", rs_file, "-o", exe_file], stderr=subprocess.STDOUT
                    )
                    result = subprocess.check_output(
                        [exe_file], stderr=subprocess.STDOUT
                    ).decode()
                    output = result

            except subprocess.CalledProcessError as e:
                output = "Rust Error:\n" + e.output.decode()

    editor_theme = request.args.get("theme", "ambiance")

    return f"""
    <html>
    <head>
        <title>Code Runner</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css">
        <link id="cm-theme-css" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/{editor_theme}.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/python/python.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/javascript/javascript.min.js"></script>
        <style>
            body {{
                background-color: #000;
                color: lightgrey;
                font-family: monospace;
                padding: 5px;
            }}
            .CodeMirror {{
                height: 250px;
                width: 100%;
                border: 3px outset #222;
                background: #000;
                color: lightgrey;
            }}
            .CodeMirror pre {{
                font-size: 15px !important;
                #font-weight: bold !important;
                line-height: 1.4 !important;
                font-family: monospace;
            }}
            .CodeMirror-linenumber {{
                font-size: 15px !important;
                font-weight: bold !important;
                line-height: 1.4 !important;
            }}
            #output {{
                width: 100%;
                height: 16em;
                font-size: 15px;
                #font-weight: bold;
                text-shadow: 0 0 2px black;
                font-family: monospace;
                background-color: white;
                color: black;
                border: 3px solid #555;
                overflow-x: auto;
                white-space: pre-wrap;
                margin-top: 4px;
                padding: 5px;
                box-sizing: border-box;
            }}
            .button-row {{
                display: flex;
                gap: 5px;
                margin-bottom: 5px;
            }}
            button.code-btn {{
                font-family: monospace, "Courier New";
                font-weight: bold;
                font-size: 20px;
                padding: 5px 0;
                background-color: #333;
                color: beige;
                border: 5px outset white;
                cursor: pointer;
                flex: 1;
                min-width: 0;
                height: 40px;
            }}
        </style>
    </head>
    <body>
        <form method="POST" id="code-form">
            <textarea id="code" name="code" spellcheck="false">{code}</textarea><br>

            <div class="button-row">
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('c')">C ></button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('bash')">Bash ></button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('javascript')">JS ></button>
                <button class="code-btn" type="button" onclick="full_view()">HTML ></button>
            </div>

            <div class="button-row">
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('golang')">Go ></button>
                <button class="code-btn" type="button" onclick="randomTheme()">Random Theme</button>
                <button class="code-btn" type="button" onclick="fileInput.click()">Open</button>
                <button class="code-btn" type="button" onclick="saveFile()">Save</button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('python')">Python ></button>
                <button class="code-btn" type="button" onclick="runCodeFormSubmission('rust')">Rust ></button>
                <input type="file" id="fileInput" style="display:none" />
            </div>

            <textarea id="output" readonly>{output}</textarea>
        </form>

        <script>
            const editor = CodeMirror.fromTextArea(document.getElementById('code'), {{
                mode: "python",
                lineNumbers: true,
                matchBrackets: true,
                autoCloseBrackets: true,
                theme: "{editor_theme}",
                tabSize: 4,
                lineWrapping: true
            }});
            editor.refresh();

            const fileInput = document.getElementById('fileInput');
            fileInput.addEventListener('change', function() {{
                const f = this.files[0];
                if (!f) return;
                const reader = new FileReader();
                reader.onload = function(e) {{
                    editor.setValue(e.target.result);
                }};
                reader.readAsText(f);
            }});

            let allowUnload = false;
            window.addEventListener("beforeunload", function(e) {{
                if (!allowUnload) {{
                    e.preventDefault();
                    e.returnValue = "";
                }}
            }});

            function runCodeFormSubmission(mode) {{
                allowUnload = true;
                const form = document.getElementById("code-form");
                const modeInput = document.createElement("input");
                modeInput.type = "hidden";
                modeInput.name = "mode";
                modeInput.value = mode;
                form.appendChild(modeInput);
                form.submit();
            }}

            function full_view() {{
                const code = editor.getValue();
                const blob = new Blob([code], {{ type: 'text/html' }});
                const url = URL.createObjectURL(blob);
                window.open(url, '_blank');
            }}

            function randomTheme() {{
                const themes = [
                    "monokai", "material", "material-darker", "material-palenight",
                    "base16-dark", "darcula", "blackboard", "abcdef", "yonce",
                    "ambiance", "mbo", "erlang-dark", "midnight", "paraiso-dark",
                    "the-matrix", "cobalt", "shadowfox", "twilight", "vibrant-ink",
                    "tomorrow-night-bright"
                ];
                const randomTheme = themes[Math.floor(Math.random() * themes.length)];
                const link = document.getElementById('cm-theme-css');
                link.href = `https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/${{randomTheme}}.min.css`;
                editor.setOption("theme", randomTheme);
            }}

            function saveFile() {{
                const code = editor.getValue();
                const blob = new Blob([code], {{ type: 'text/plain' }});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = "code.txt";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }}
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(port=8300, debug=False)
