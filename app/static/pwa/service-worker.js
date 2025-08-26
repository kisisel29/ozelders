const CACHE_NAME = 'math-tutor-v1';
const urlsToCache = [
  '/',
  '/static/css/tailwind.css',
  '/static/js/app.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip API requests for cache-first strategy
  if (event.request.url.includes('/api/')) {
    // Network first for API requests
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Clone the response
          const responseToCache = response.clone();
          
          // Only cache successful responses
          if (response.status === 200) {
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
          }
          
          return response;
        })
        .catch(() => {
          // If network fails, try to serve from cache
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache first for static resources
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request).then((response) => {
          // Clone the response
          const responseToCache = response.clone();
          
          // Open cache and store the response
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
      .catch(() => {
        // If both cache and network fail, show offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return new Response(
            `
            <!DOCTYPE html>
            <html>
              <head>
                <title>Offline - Math Tutor</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <script src="https://cdn.tailwindcss.com"></script>
              </head>
              <body class="bg-gray-50 flex items-center justify-center min-h-screen">
                <div class="text-center p-6">
                  <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                    </svg>
                  </div>
                  <h1 class="text-2xl font-bold text-gray-900 mb-2">You're Offline</h1>
                  <p class="text-gray-600 mb-4">Please check your internet connection and try again.</p>
                  <button onclick="window.location.reload()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Try Again
                  </button>
                </div>
              </body>
            </html>
            `,
            {
              headers: { 'Content-Type': 'text/html' }
            }
          );
        }
      })
  );
});

// Background sync for offline submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync-submissions') {
    event.waitUntil(syncSubmissions());
  }
});

async function syncSubmissions() {
  // This would handle syncing offline submissions when connection is restored
  console.log('Syncing offline submissions...');
}

// Push notifications (if needed in the future)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New notification from Math Tutor',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'explore',
        title: 'View',
        icon: '/static/icons/icon-72x72.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/icon-72x72.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Math Tutor', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'explore') {
    clients.openWindow('/student/home');
  }
});