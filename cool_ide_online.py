from flask import Flask, request
import subprocess
import tempfile
import os

app = Flask(__name__)

saved_html = "<h1>No HTML loaded</h1>"
                                        @app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/ambiance.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/python/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/rust/rust.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/go/go.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/xml/xml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/htmlmixed/htmlmixed.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/clike/clike.min.js"></script>

<style>
body {
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: Arial;
    background: white;
    padding-top: 14px;
}

#topWindow {
    width: 95%;
    margin-bottom: 15px;
}

.CodeMirror {
    width: 100% !important;
    height: 300px;
    font-size: 14px;
    font-family: monospace;
    font-weight: bold;
    border: 3px solid black;
    border-radius: 4px;
    box-sizing: border-box;
}

#bottomWindow {
    width: 95%;
    height: 600px;
    font-size: 15px;
    font-family: monospace;
    font-weight: bold;
    border: 3px solid black;
    border-radius: 4px;
    padding: 6px;
    margin-bottom: 15px;
    background: #ffffff;
    color: #000000;
    box-sizing: border-box;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-break: break-word;
    outline: none;
}

#buttonRow {
    width: 95%;
    display: flex;
    gap: 4px;
    margin-bottom: 15px;
}

.btn {
    flex: 1;
    height: 50px;
    font-size: 18px;
    font-family: "Courier New";
    font-weight: bold;
    border: 2px solid black;
    border-radius: 12px;
    background: lightyellow;
    color: black;
    cursor: pointer;
}

.btn:active {
    transform: scale(0.96);
    background: #111827;
}

html, body {
    overscroll-behavior: none;
}

body {
    overscroll-behavior-y: contain;
}
</style>

<script>
let editor;

function getCode() {
    return editor.getValue();
}

function setCode(text) {
    editor.setValue(text);
}

function insertAtCursor(text) {
    const doc = editor.getDoc();
    const cursor = doc.getCursor();
    doc.replaceRange(text, cursor);
}

function runHTML() {
    const code = getCode();

    fetch("/set_html", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: "html=" + encodeURIComponent(code)
    }).then(() => {
        window.open("/view_html", "_blank");
    });
}

function runPython() {
    const code = getCode();

    fetch("/run_python", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: "code=" + encodeURIComponent(code)
    })
    .then(r => r.text())
    .then(data => {
        document.getElementById("bottomWindow").innerText = data;
    });
}

function runRust() {
    const code = getCode();

    fetch("/run_rust", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: "code=" + encodeURIComponent(code)
    })
    .then(r => r.text())
    .then(data => {
        document.getElementById("bottomWindow").innerText = data;
    });
}

function runGo() {
    const code = getCode();

    fetch("/run_go", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: "code=" + encodeURIComponent(code)
    })
    .then(r => r.text())
    .then(data => {
        document.getElementById("bottomWindow").innerText = data;
    });
}

function runCpp() {
    const code = getCode();

    fetch("/run_cpp", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: "code=" + encodeURIComponent(code)
    })
    .then(r => r.text())
    .then(data => {
        document.getElementById("bottomWindow").innerText = data;
    });
}

window.onload = function() {
    editor = CodeMirror(document.getElementById("topWindow"), {
        value: "",
        mode: "text/x-python",
        theme: "ambiance",

        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        autofocus: true
    });

    editor.setSize("100%", 320);
    editor.focus();
};
</script>

</head>

<body>

<div id="topWindow"></div>

<div id="buttonRow">
    <button class="btn" onclick="runRust()">Rust</button>
    <button class="btn" onclick="runGo()">Go ></button>
    <button class="btn" onclick="runCpp()">C++</button>
    <button class="btn" onclick="runPython()">P ></button>
    <button class="btn" onclick="runHTML()">HTML</button>
</div>

<div id="bottomWindow" class="window" contenteditable="true"></div>

</body>
</html>
"""

@app.route("/set_html", methods=["POST"])
def set_html():
    global saved_html
    saved_html = request.form.get("html", "")
    return "ok"

@app.route("/view_html")
def view_html():
    return saved_html

@app.route("/run_python", methods=["POST"])
def run_python():
    code = request.form.get("code", "")

    result = subprocess.run(
        ["python3", "-q", "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=5
    )

    if result.returncode != 0:
        return result.stderr.splitlines()[-1]

    return result.stdout

@app.route("/run_rust", methods=["POST"])
def run_rust():
    code = request.form.get("code", "")
    tmp = None
    exe = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".rs") as f:
            f.write(code.encode())
            tmp = f.name

        exe = tmp.replace(".rs", "")

        subprocess.check_output(["rustc", tmp, "-o", exe], stderr=subprocess.STDOUT)
        result = subprocess.check_output([exe], stderr=subprocess.STDOUT).decode()
        return result
    except subprocess.CalledProcessError as e:
        return e.output.decode()
    finally:
        for p in [tmp, exe]:
            if p and os.path.exists(p):
                os.remove(p)

@app.route("/run_go", methods=["POST"])
def run_go():
    code = request.form.get("code", "")
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".go") as f:
            f.write(code.encode())
            tmp = f.name

        result = subprocess.check_output(
            ["go", "run", tmp],
            stderr=subprocess.STDOUT
        ).decode()

        return result
    except subprocess.CalledProcessError as e:
        return e.output.decode()
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)

@app.route("/run_cpp", methods=["POST"])
def run_cpp():
    code = request.form.get("code", "")
    cpp_file = None
    exe_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as f:
            f.write(code.encode())
            cpp_file = f.name

        exe_file = cpp_file[:-4]

        compile_result = subprocess.run(
            ["g++", cpp_file, "-o", exe_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        if compile_result.returncode != 0:
            return compile_result.stderr

        run_result = subprocess.run(
            [exe_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )

        if run_result.returncode != 0:
            return run_result.stderr

        return run_result.stdout
    except subprocess.TimeoutExpired:
        return "timeout"
    except Exception as e:
        return str(e)
    finally:
        for p in [cpp_file, exe_file]:
            if p and os.path.exists(p):
                os.remove(p)

if __name__ == "__main__":
    app.run(port=8600)
