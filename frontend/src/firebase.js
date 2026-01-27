// Firebase configuration for LegalConnect
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
    apiKey: "AIzaSyAFIp4YXpI_XBQ4xSYt_PjiOUpbcNVDdF8",
    authDomain: "legalconnect-b2797.firebaseapp.com",
    projectId: "legalconnect-b2797",
    storageBucket: "legalconnect-b2797.firebasestorage.app",
    messagingSenderId: "956541502717",
    appId: "1:956541502717:web:808ed8444bebfd2f5bea94",
    measurementId: "G-HK5SSMML1W"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

export default app;
