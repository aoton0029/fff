/**
 * upload.js — drag-and-drop file upload component
 * Supports multiple file selection; builds a DataTransfer to attach to the hidden input.
 */
(function () {
  'use strict';

  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');
  const clearBtn = document.getElementById('clearFiles');

  if (!dropZone || !fileInput) return;

  let selectedFiles = [];

  function renderFileList() {
    fileList.innerHTML = '';
    selectedFiles.forEach(function (file, idx) {
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-center py-1';
      li.innerHTML =
        '<span><i class="bi bi-file-earmark-excel text-success me-2"></i>' +
        escapeHtml(file.name) +
        ' <span class="text-muted small">(' + formatBytes(file.size) + ')</span></span>' +
        '<button type="button" class="btn btn-sm btn-outline-danger py-0 px-1" data-idx="' + idx + '">' +
        '<i class="bi bi-x-lg"></i></button>';
      fileList.appendChild(li);
    });

    // Sync DataTransfer → input.files
    const dt = new DataTransfer();
    selectedFiles.forEach(function (f) { dt.items.add(f); });
    fileInput.files = dt.files;
  }

  function addFiles(newFiles) {
    Array.from(newFiles).forEach(function (f) {
      if (f.name.match(/\.(xlsx|xls)$/i)) {
        selectedFiles.push(f);
      }
    });
    renderFileList();
  }

  // Click to open dialog
  dropZone.addEventListener('click', function () { fileInput.click(); });

  fileInput.addEventListener('change', function () {
    addFiles(fileInput.files);
  });

  // Drag events
  dropZone.addEventListener('dragover', function (e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });
  dropZone.addEventListener('dragleave', function () {
    dropZone.classList.remove('drag-over');
  });
  dropZone.addEventListener('drop', function (e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    addFiles(e.dataTransfer.files);
  });

  // Remove individual file
  fileList.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-idx]');
    if (!btn) return;
    const idx = parseInt(btn.dataset.idx, 10);
    selectedFiles.splice(idx, 1);
    renderFileList();
  });

  // Clear all
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      selectedFiles = [];
      fileInput.value = '';
      renderFileList();
    });
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // Clear alert area before each upload request
  document.body.addEventListener('htmx:beforeRequest', function (evt) {
    var alertArea = document.getElementById('upload-alert-area');
    if (alertArea) alertArea.innerHTML = '';
  });

  // Clear selected files after upload completes (success or failure)
  document.body.addEventListener('htmx:afterRequest', function (evt) {
    if (evt.detail.elt && evt.detail.elt.id === 'uploadForm') {
      selectedFiles = [];
      fileInput.value = '';
      renderFileList();
    }
  });

  // After HTMX OOB swap populates the alert area, open the accordion
  document.body.addEventListener('htmx:afterSettle', function () {
    var alertArea = document.getElementById('upload-alert-area');
    if (alertArea && alertArea.innerHTML.trim() !== '') {
      var collapseEl = document.getElementById('uploadCollapse');
      if (collapseEl && !collapseEl.classList.contains('show')) {
        var bsCollapse = bootstrap.Collapse.getInstance(collapseEl)
                         || new bootstrap.Collapse(collapseEl, { toggle: false });
        bsCollapse.show();
      }
    }
  });
})();
