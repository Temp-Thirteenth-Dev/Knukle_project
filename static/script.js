const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const preview = document.getElementById('preview');
const dropzoneText = document.getElementById('dropzone-text');
const tabs = document.querySelectorAll('.tab');
const mainBtn = document.getElementById('main-btn');
const vizBtn = document.getElementById('viz-btn');
const resultBox = document.getElementById('result-box');
const vizImg = document.getElementById('visualize-img');
const loader = document.getElementById('loader');
const btnText = document.getElementById('btn-text');

let currentMode = 'verify'; // 'register' or 'verify'
let selectedFile = null;

// Tab Switching
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentMode = tab.dataset.mode;
        
        mainBtn.innerHTML = currentMode === 'register' ? 
            '<span id="btn-text">Register User</span><div id="loader" class="loader"></div>' : 
            '<span id="btn-text">Verify Identity</span><div id="loader" class="loader"></div>';
            
        vizBtn.style.display = currentMode === 'verify' ? 'block' : 'none';
        
        // Reset state
        resultBox.style.display = 'none';
        vizImg.style.display = 'none';
    });
});

// Drag and Drop
dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    if (!file.type.startsWith('image/')) return;
    selectedFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        preview.style.display = 'block';
        dropzoneText.style.display = 'none';
    }
    reader.readAsDataURL(file);
    resultBox.style.display = 'none';
    vizImg.style.display = 'none';
}

function setLoading(isLoading) {
    const loaderEl = document.getElementById('loader');
    const txtEl = document.getElementById('btn-text');
    if (isLoading) {
        if(loaderEl) loaderEl.style.display = 'block';
        if(txtEl) txtEl.style.display = 'none';
        mainBtn.disabled = true;
    } else {
        if(loaderEl) loaderEl.style.display = 'none';
        if(txtEl) txtEl.style.display = 'block';
        mainBtn.disabled = false;
    }
}

function showResult(success, message) {
    resultBox.textContent = message;
    resultBox.className = success ? 'success' : 'error';
    resultBox.style.display = 'block';
}

mainBtn.addEventListener('click', async () => {
    const userId = document.getElementById('user_id').value.trim();
    if (!userId) return showResult(false, 'Please enter a User ID');
    if (!selectedFile) return showResult(false, 'Please select an image');

    setLoading(true);
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('image', selectedFile);

    try {
        const endpoint = currentMode === 'register' ? '/api/register' : '/api/verify';
        const res = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        showResult(data.success, data.message);
    } catch (err) {
        showResult(false, 'Network error occurred');
    }
    setLoading(false);
});

vizBtn.addEventListener('click', async () => {
    const userId = document.getElementById('user_id').value.trim();
    if (!userId) return showResult(false, 'Please enter a User ID');
    if (!selectedFile) return showResult(false, 'Please select an image');

    const originalText = vizBtn.textContent;
    vizBtn.textContent = 'Visualizing...';
    vizBtn.disabled = true;

    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('image', selectedFile);

    try {
        const res = await fetch('/api/visualize', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        if (data.success) {
            vizImg.src = `data:image/png;base64,${data.image}`;
            vizImg.style.display = 'block';
            showResult(true, `Found ${data.matches} SIFT matches!`);
        } else {
            showResult(false, data.message);
        }
    } catch (err) {
        showResult(false, 'Visualization failed');
    }
    
    vizBtn.textContent = originalText;
    vizBtn.disabled = false;
});
