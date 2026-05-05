function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function ensureToastRoot() {
  let root = document.getElementById('toastRoot');
  if (root) return root;
  root = document.createElement('div');
  root.id = 'toastRoot';
  root.className = 'toast-root';
  root.setAttribute('aria-live', 'polite');
  document.body.appendChild(root);
  return root;
}

function showToast(message, type = 'info') {
  const root = ensureToastRoot();
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  root.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('hide');
    setTimeout(() => toast.remove(), 250);
  }, 2200);
}

function clearFieldErrors(form) {
  form.querySelectorAll('.form-error').forEach((el) => el.remove());
  form.querySelectorAll('.has-error').forEach((el) => el.classList.remove('has-error'));
}

function setFieldError(form, fieldName, message) {
  const field = form.querySelector(`[name="${fieldName}"]`);
  if (!field) return;
  const group = field.closest('.form-group') || field.parentElement;
  if (group) group.classList.add('has-error');
  const error = document.createElement('div');
  error.className = 'form-error';
  error.textContent = message;
  if (group) {
    group.appendChild(error);
  } else {
    field.insertAdjacentElement('afterend', error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('commentForm');
  if (!form) return;
  const parentInput = document.getElementById('parent_id');
  const replyBanner = document.getElementById('replyBanner');
  const replyText = document.getElementById('replyText');
  const cancelReplyBtn = document.getElementById('cancelReplyBtn');
  const commentsList = document.querySelector('.comments-list');
  const textarea = document.getElementById('content');

  commentsList.addEventListener('click', (e) => {
    const btn = e.target.closest('.comment-reply-btn');
    if (!btn) return;
    const cid = btn.getAttribute('data-comment-id');
    const name = btn.getAttribute('data-reply-to');
    parentInput.value = cid || '';
    replyText.textContent = `回复 @${name}`;
    replyBanner.style.display = 'block';
    if (textarea) textarea.focus();
  });

  cancelReplyBtn.addEventListener('click', () => {
    parentInput.value = '';
    replyBanner.style.display = 'none';
    replyText.textContent = '';
  });

  if (textarea) {
    textarea.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        form.requestSubmit();
      }
      if (e.key === 'Escape') {
        cancelReplyBtn.click();
      }
    });
  }

  form.addEventListener('submit', async (e) => {
    if (form.dataset.ajax !== 'true') return;
    e.preventDefault();
    clearFieldErrors(form);
    const csrf = getCookie('csrftoken');
    const data = new FormData(form);
    const url = window.COMMENT_CFG && window.COMMENT_CFG.ajaxUrl ? window.COMMENT_CFG.ajaxUrl : form.action;
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.dataset.originalText = submitBtn.textContent;
      submitBtn.textContent = '提交中...';
    }
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrf || ''
        },
        body: data
      });
      const json = await res.json();
      if (!res.ok || !json.ok) {
        if (json && json.error === 'rate_limited') {
          showToast('提交太快啦，休息 10 秒再来～', 'warn');
        } else if (json && json.errors) {
          Object.entries(json.errors).forEach(([field, msgs]) => {
            if (Array.isArray(msgs) && msgs.length) {
              setFieldError(form, field, msgs[0]);
            }
          });
          showToast('请检查表单填写', 'error');
        } else {
          showToast('提交失败，请稍后重试', 'error');
        }
      } else {
        if (json.html) {
          if (json.parent_id) {
            const parent = document.querySelector(`.comment-item[data-comment-id="${json.parent_id}"] .comment-replies`);
            if (parent) {
              const temp = document.createElement('div');
              temp.innerHTML = json.html;
              const node = temp.firstElementChild;
              parent.appendChild(node);
              node.scrollIntoView({ behavior: 'smooth', block: 'center' });
              node.classList.add('comment-flash');
              setTimeout(() => node.classList.remove('comment-flash'), 700);
            }
          } else {
            const temp = document.createElement('div');
            temp.innerHTML = json.html;
            const node = temp.firstElementChild;
            commentsList.insertBefore(node, commentsList.firstChild);
            node.scrollIntoView({ behavior: 'smooth', block: 'center' });
            node.classList.add('comment-flash');
            setTimeout(() => node.classList.remove('comment-flash'), 700);
          }
        }
        form.reset();
        parentInput.value = '';
        replyBanner.style.display = 'none';
        showToast('评论已提交，审核通过后显示', 'success');
      }
    } catch (err) {
      showToast('网络异常，请稍后再试', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        if (submitBtn.dataset.originalText) {
          submitBtn.textContent = submitBtn.dataset.originalText;
        }
      }
    }
  });
});
