function clearError() {
  const el = document.getElementById('formError');
  if (el) el.textContent = '';
}

function setError(message) {
  const el = document.getElementById('formError');
  if (el) el.textContent = message;
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes < 0) return '';
  const kb = bytes / 1024;
  if (kb < 1024) return `${Math.round(kb)} KB`;
  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}

function isAllowedImageType(file) {
  const name = String(file?.name ?? '').toLowerCase();
  return (
    name.endsWith('.jpg') ||
    name.endsWith('.jpeg') ||
    name.endsWith('.png') ||
    name.endsWith('.webp')
  );
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('imageForm');
  if (!form) return;

  const fileInput = document.getElementById('image');
  const previewWrap = document.getElementById('imagePreviewWrap');
  const previewImg = document.getElementById('imagePreview');
  const previewMeta = document.getElementById('imageMeta');

  let previewUrl = null;

  function clearPreview() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = null;
    }
    if (previewWrap) previewWrap.hidden = true;
    if (previewImg) previewImg.removeAttribute('src');
    if (previewMeta) previewMeta.textContent = '';
  }

  function setPreview(file) {
    clearPreview();
    if (!file) return;
    previewUrl = URL.createObjectURL(file);
    if (previewImg) previewImg.src = previewUrl;
    if (previewMeta) previewMeta.textContent = `${file.name} • ${formatBytes(file.size)}`;
    if (previewWrap) previewWrap.hidden = false;
  }

  fileInput?.addEventListener('change', () => {
    clearError();
    const file = fileInput.files?.[0] ?? null;
    if (!file) {
      clearPreview();
      return;
    }
    if (!isAllowedImageType(file)) {
      setError('Please select a JPG, PNG, or WebP image.');
      fileInput.value = '';
      clearPreview();
      return;
    }
    setPreview(file);
  });

  form.addEventListener('submit', (e) => {
    clearError();
    const file = fileInput?.files?.[0] ?? null;
    if (!file) {
      e.preventDefault();
      setError('Please choose an image to upload.');
      return;
    }
    if (!isAllowedImageType(file)) {
      e.preventDefault();
      setError('Please select a JPG, PNG, or WebP image.');
    }
  });

  window.addEventListener('beforeunload', () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
  });
});
