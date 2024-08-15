document.getElementById('file-input').addEventListener('change', function() {
    var fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    
    for (var i = 0; i < this.files.length; i++) {
        var listItem = document.createElement('div');
        listItem.textContent = this.files[i].name;
        fileList.appendChild(listItem);
    }
});

document.getElementById('upload-form').addEventListener('submit', function(event) {
    var fileInput = document.getElementById('file-input');
    if (fileInput.files.length === 0) {
        alert('Please select at least one file to upload.');
        event.preventDefault();
    }
});
