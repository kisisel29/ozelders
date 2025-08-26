// Firebase configuration (replace with your actual config)
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Global auth state
let currentUser = null;

// Auth state listener
firebase.auth().onAuthStateChanged((user) => {
  currentUser = user;
  if (user) {
    // User is signed in
    console.log('User signed in:', user.email);
  } else {
    // User is signed out
    console.log('User signed out');
  }
});

// Sign out function
function signOut() {
  firebase.auth().signOut().then(() => {
    window.location.href = '/';
  });
}

// Toast notification function
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const colors = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500'
  };
  
  toast.className = `${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
  toast.textContent = message;
  
  document.getElementById('toast-container').appendChild(toast);
  
  // Animate in
  setTimeout(() => toast.classList.remove('translate-x-full'), 100);
  
  // Remove after 5 seconds
  setTimeout(() => {
    toast.classList.add('translate-x-full');
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

// HTMX event listeners
document.addEventListener('htmx:afterRequest', function(event) {
  if (event.detail.xhr.status >= 400) {
    showToast('An error occurred. Please try again.', 'error');
  }
});

// Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/pwa/service-worker.js')
      .then(registration => {
        console.log('SW registered: ', registration);
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// PWA Install prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent Chrome 67 and earlier from automatically showing the prompt
  e.preventDefault();
  // Stash the event so it can be triggered later.
  deferredPrompt = e;
  
  // Show install button
  const installButton = document.getElementById('install-button');
  if (installButton) {
    installButton.style.display = 'block';
    
    installButton.addEventListener('click', (e) => {
      // Hide the install button
      installButton.style.display = 'none';
      // Show the install prompt
      deferredPrompt.prompt();
      // Wait for the user to respond to the prompt
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted the install prompt');
        } else {
          console.log('User dismissed the install prompt');
        }
        deferredPrompt = null;
      });
    });
  }
});

// Online/Offline status
window.addEventListener('online', () => {
  showToast('You are back online!', 'success');
});

window.addEventListener('offline', () => {
  showToast('You are now offline. Some features may be limited.', 'warning');
});

// Utility functions for forms
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Auto-save functionality for forms
function enableAutoSave(formSelector, saveEndpoint, interval = 30000) {
  const form = document.querySelector(formSelector);
  if (!form) return;
  
  let saveTimeout;
  
  const saveForm = async () => {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    try {
      const token = await firebase.auth().currentUser.getIdToken();
      const response = await fetch(saveEndpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (response.ok) {
        console.log('Form auto-saved');
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  };
  
  form.addEventListener('input', () => {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(saveForm, interval);
  });
  
  // Save before unload
  window.addEventListener('beforeunload', saveForm);
}

// Math utilities
const MathUtils = {
  formatNumber: (num) => {
    return new Intl.NumberFormat().format(num);
  },
  
  percentage: (value, total) => {
    return total > 0 ? Math.round((value / total) * 100) : 0;
  },
  
  average: (numbers) => {
    if (numbers.length === 0) return 0;
    return numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
  }
};

// Export for use in other scripts
window.MathTutor = {
  showToast,
  formatFileSize,
  enableAutoSave,
  MathUtils
};