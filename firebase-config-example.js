// Firebase konfigürasyon örneği
// Bu dosyayı kopyalayıp firebase-config.js olarak adlandırın ve kendi Firebase bilgilerinizle güncelleyin

const firebaseConfig = {
  apiKey: "your-api-key-here",
  authDomain: "your-project-id.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project-id.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id-here"
};

// Firebase'i başlat
firebase.initializeApp(firebaseConfig);

// Auth ve Storage servislerini export et
const auth = firebase.auth();
const storage = firebase.storage();

export { auth, storage };
