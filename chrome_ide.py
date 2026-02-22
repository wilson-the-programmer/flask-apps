from flask import Flask, request, render_template_string
import subprocess
import tempfile
import os
app = Flask(__name__)
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>My Computer</title>
<meta charset="UTF-8">

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/theme/ambiance.min.css">

<style>
body {
    background: #1e1e1e;
    color: #e5e5e5;
    font-family: monospace;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
}
.container {
    width: 95%;
    max-width: 940px;
    padding: 25px;
}
.CodeMirror {
    height: 620px;
    font-size: 15px;
    font-weight: bold;
    border: 3px solid white;
}
.CodeMirror-scroll {
    padding: 14px;
    box-sizing: border-box;
}
select, button {
    padding: 14px 18px;
    font-size: 68px;
    font-weight: bold;
    margin-top: 12px;
    background-color: black;
    color: orange;
}
.output-box {
    width: 96%;
    height: 540px;
    background: white;
    color: black;
    font-weight: bold;
    text-shadow: 0 0 2px black;
    border: 1px solid #444;
    padding: 14px;
    margin-top: 20px;
    font-size: 45px;
    white-space: pre-wrap;
    overflow-wrap: break-word;
    word-break: break-word;
    overflow-y: scroll;
}
button {
    background-color: black;
    color: white;
    border: 2px solid lightgrey;
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 68px;
    margin-top: 12px;
    cursor: pointer;
    transition: background-color 0.2s, color 0.2s;
}
button:hover {
    background-color: #222;
    color: #aaffaa;
    border-color: lightgrey;
}
.shortcut-btn {
    display: inline-block;
    margin-left: 12px;
    margin-top: 12px;
    font-size: 68px;
    background-color: yellow;
    color: blue;
    border-radius: 12px;
    border: 2px solid blue;
}
.shortcut-btn:hover {
    background-color: #ffff99;
    color: #0000cc;
}
</style>
</head>
<body>
<div class="container">

<form method="post" id="code-form">
    <textarea id="code" name="code">{{ code }}</textarea><br>
    <select name="mode" id="mode">
        <option value="python" {% if mode=='python' %}selected{% endif %}>Python</option>
        <option value="rust" {% if mode=='rust' %}selected{% endif %}>Rust</option>
        <option value="c" {% if mode=='c' %}selected{% endif %}>C</option>
        <option value="sh" {% if mode=='sh' %}selected{% endif %}>Bash</option>
    </select>

    <button type="button" id="open-btn">Open</button>
    <button type="button" id="save-btn">Save</button>
    <button type="button" id="sys-btn">Sys</button>
    <button type="button" id="clear-btn">Cls</button>
    <button type="submit" id="run-btn">Run</button>

    <button type="button" class="shortcut-btn" id="bash-btn">B></button>
    <button type="button" class="shortcut-btn" id="c-btn">C></button>
    <button type="button" class="shortcut-btn" id="python-btn">P></button>
    <button type="button" class="shortcut-btn" id="rust-btn">R></button>
</form>

<input type="file" id="file-input" style="display:none;">

<div class="output-box" id="output">{{ output }}</div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/python/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/rust/rust.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/clike/clike.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/shell/shell.min.js"></script>

<script>
const textarea = document.getElementById('code');
const modeSelect = document.getElementById('mode');
const form = document.getElementById('code-form');
const fileInput = document.getElementById('file-input');
const openBtn = document.getElementById('open-btn');
const saveBtn = document.getElementById('save-btn');
const sysBtn = document.getElementById('sys-btn');
const clearBtn = document.getElementById('clear-btn');

const bashBtn = document.getElementById('bash-btn');
const cBtn = document.getElementById('c-btn');
const pythonBtn = document.getElementById('python-btn');
const rustBtn = document.getElementById('rust-btn');

const editor = CodeMirror.fromTextArea(textarea, {
    lineNumbers: false,
    theme: 'ambiance',
    lineWrapping: true,
    smartIndent: false
});

editor.setSize("100%", "635px");

function updateMode() {
    const mode = modeSelect.value;
    let cmMode = 'python';
    if(mode === 'python') cmMode = 'python';
    else if(mode === 'rust') cmMode = 'rust';
    else if(mode === 'c') cmMode = 'text/x-csrc';
    else if(mode === 'sh') cmMode = 'shell';
    editor.setOption('mode', cmMode);
}

modeSelect.addEventListener('change', updateMode);
updateMode();

form.addEventListener('submit', function() {
    textarea.value = editor.getValue();
});

openBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
        editor.setValue(ev.target.result);
    };
    reader.readAsText(file);
});

saveBtn.addEventListener('click', () => {
    const blob = new Blob([editor.getValue()], {type: 'text/plain'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'code.txt';
    a.click();
    URL.revokeObjectURL(a.href);
});

clearBtn.addEventListener('click', () => editor.setValue(''));

sysBtn.addEventListener('click', () => {
    const doc = editor.getDoc();
    const cursor = doc.getCursor();
    const lineNumber = cursor.line;
    const commandLine = doc.getLine(lineNumber).trim();
    if(!commandLine) return;

    fetch(`/sys_command?cmd=${encodeURIComponent(commandLine)}`)
        .then(res => res.text())
        .then(output => {
            doc.replaceRange('\\n' + output + '\\n', {line: lineNumber + 1, ch: 0});
        });
});

function runCode(mode) {
    modeSelect.value = mode;
    updateMode();

    const code = editor.getValue();
    const formData = new URLSearchParams();
    formData.append('code', code);
    formData.append('mode', mode);

    fetch("/", {
        method: "POST",
        body: formData,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    })
    .then(res => res.text())
    .then(html => {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const newOutput = tempDiv.querySelector('#output').innerHTML;
        document.getElementById('output').innerHTML = newOutput;
    });
}

bashBtn.addEventListener('click', () => runCode('sh'));
cBtn.addEventListener('click', () => runCode('c'));
pythonBtn.addEventListener('click', () => runCode('python'));
rustBtn.addEventListener('click', () => runCode('rust'));
</script>
</body>
</html>
"""
@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    output = ""
    mode = "python"

    if request.method == "POST":
        code = request.form.get("code", "")
        mode = request.form.get("mode", "")

        if mode == "python":
            try:
                result = subprocess.check_output(["python3", "-c", code], stderr=subprocess.STDOUT)
                output = result.decode()
            except subprocess.CalledProcessError as e:
                output = e.output.decode()

        elif mode == "rust":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".rs") as tmp:
                tmp.write(code.encode())
                tmp.flush()
                exe = tmp.name + ".out"
                comp = subprocess.run(["rustc", tmp.name, "-o", exe], capture_output=True)
                if comp.returncode != 0:
                    output = comp.stderr.decode()
                else:
                    run = subprocess.run([exe], capture_output=True)
                    output = run.stdout.decode() + run.stderr.decode()
                os.unlink(tmp.name)
                if os.path.exists(exe):
                    os.unlink(exe)

        elif mode == "c":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tmp:
                tmp.write(code.encode())
                tmp.flush()
                exe = tmp.name + ".out"
                comp = subprocess.run(["gcc", tmp.name, "-o", exe], capture_output=True)
                if comp.returncode != 0:
                    output = comp.stderr.decode()
                else:
                    run = subprocess.run([exe], capture_output=True)
                    output = run.stdout.decode() + run.stderr.decode()
                os.unlink(tmp.name)
                if os.path.exists(exe):
                    os.unlink(exe)

        elif mode == "sh":
            try:
                result = subprocess.check_output(code, shell=True, stderr=subprocess.STDOUT, executable="/bin/bash")
                output = result.decode()
            except subprocess.CalledProcessError as e:
                output = e.output.decode()

    return render_template_string(HTML, code=code, output=output, mode=mode)

@app.route("/sys_command")
def sys_command():
    cmd = request.args.get("cmd", "")
    if not cmd.strip():
        return ""
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, executable="/bin/bash")
        return result.decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()

if __name__ == "__main__":
    app.run(port=9000, debug=False)