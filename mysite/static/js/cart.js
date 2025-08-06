//console.log('[加入購物車]', { attractionId, title });


// cart.js 模組
export function addToCart(attractionId, title = '', btn = null) {
  if (!attractionId) {
    console.warn('⚠️ attractionId 不存在');
    return showToast('資料錯誤，無法加入購物車', true);
  }
  fetch('/myapp/index/add/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ id: attractionId })
  })
  .then(res => {
    if (!res.ok) throw new Error('非 200 回應');
    return res.json();
  })

  .then(data => {
    console.log('成功加入購物車：', data);
    if (data.success) {
      showToast(`${title || '項目'} 已加入購物車 🛒`);
      if (btn) {
        btn.classList.add('added');
      }
    } else {
      showToast(`加入失敗：${data.message}`, true);
      if (data.message.includes('已加入過')) {
        alert('此項目已在購物車中');
      }
    }
  })
  .catch(err => {
    console.error('[加入購物車失敗]', err);
    showToast('系統錯誤，請稍後再試', true);
  });
  }


// 提示訊息（toast）範例
function showToast(message, isError = false) {
  const toast = document.createElement('div');
  toast.className = `custom-toast ${isError ? 'error' : 'success'}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}

// CSRF 工具（如你已有可跳過）
function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='));
  return cookieValue?.split('=')[1];
}