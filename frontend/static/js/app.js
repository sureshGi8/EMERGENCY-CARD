// Configuration
const API_URL = 'https://emergency-card-backend.onrender.com';
let authToken = localStorage.getItem('authToken');
let currentUser = null;
let currentCardData = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        loadUserData();
    }
});

// Show/Hide Loading
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Show Toast
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Toggle Auth Forms
function toggleAuthForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    showLoading();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showToast('Login successful!', 'success');
            await loadUserData();
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Handle Register
async function handleRegister(event) {
    event.preventDefault();
    showLoading();
    
    const full_name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name, phone })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showToast('Registration successful!', 'success');
            await loadUserData();
        } else {
            showToast(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Load User Data
async function loadUserData() {
    try {
        const response = await fetch(`${API_URL}/api/user/me?token=${authToken}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        
        currentUser = await response.json();
        
        // Show app section
        document.getElementById('authSection').style.display = 'none';
        document.getElementById('appSection').style.display = 'block';
        document.getElementById('navbar').style.display = 'block';
        
        // Update dashboard
        document.getElementById('userNameDisplay').textContent = currentUser.full_name;
        
        // Load all data
        await loadProfile();
        await loadContacts();
        await loadLogs();
        
        showSection('dashboard');
    } catch (error) {
        console.error('Error loading user data:', error);
        showToast('Error loading app', 'error');
        logout();
    }
}

// Load Profile
async function loadProfile() {
    try {
        const response = await fetch(`${API_URL}/api/profile?token=${authToken}`);
        
        if (response.ok) {
            const data = await response.json();
            const profile = data.profile;
            
            const bloodGroupDisplay = document.getElementById('bloodGroupDisplay');
            if (bloodGroupDisplay) {
                bloodGroupDisplay.textContent = profile?.blood_group || '-';
            }
            
            if (profile) {
                // Load emergency card
                await loadEmergencyCard();
                
                // Fill form fields
                const fields = {
                    'age': profile.age || '',
                    'gender': profile.gender || '',
                    'bloodGroup': profile.blood_group || '',
                    'height': profile.height || '',
                    'weight': profile.weight || '',
                    'address': profile.address || '',
                    'allergies': profile.allergies || '',
                    'medicalConditions': profile.medical_conditions || '',
                    'medications': profile.medications || '',
                    'medicalNotes': profile.medical_notes || ''
                };
                
                for (const [id, value] of Object.entries(fields)) {
                    const element = document.getElementById(id);
                    if (element) {
                        element.value = value;
                    }
                }
            } else {
                const cardSection = document.getElementById('cardSection');
                if (cardSection) {
                    cardSection.style.display = 'none';
                }
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Load Emergency Card and Display It
async function loadEmergencyCard() {
    try {
        const response = await fetch(`${API_URL}/api/card/data?token=${authToken}`);
        
        if (response.ok) {
            const cardData = await response.json();
            currentCardData = cardData;
            
            // Show card section
            const cardSection = document.getElementById('cardSection');
            if (cardSection) {
                cardSection.style.display = 'block';
            }
            
            // Generate and display card
            generateCardHTML(cardData);
        }
    } catch (error) {
        console.error('Error loading emergency card:', error);
    }
}

// Generate Card HTML
function generateCardHTML(cardData) {
    const primaryContactText = cardData.primary_contact 
        ? `${cardData.primary_contact.name} - ${cardData.primary_contact.phone}`
        : 'None';
    
    // QR URL points to Type 1 detailed card
    const qrDataUrl = `https://emergency-card-backend.onrender.com/emergency/${cardData.profile_id}/type1`;
    const qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrDataUrl)}`;
    
    const cardHTML = `
        <div class="wallet-card" id="downloadable-card">
            <div class="medical-icon">⚕️</div>
            <div class="card-title">EMERGENCY INFORMATION</div>
            <div class="card-subtitle">Critical Medical Data</div>
            <div class="card-content">
                <div class="info-section">
                    <div class="info-row">
                        <div class="info-label">NAME</div>
                        <div class="info-value">${cardData.user_name}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">AGE</div>
                        <div class="info-value">${cardData.age} years</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">BLOOD TYPE</div>
                        <div class="info-value blood-display">${cardData.blood_group}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">EMERGENCY CONTACT</div>
                        <div class="info-value" style="font-size: 13px;">${primaryContactText}</div>
                    </div>
                </div>
                <div class="barcode-section">
                    <img src="${qrImageUrl}" alt="QR Code" class="barcode-image" crossorigin="anonymous">
                    <div class="barcode-text">SCAN FOR<br>FULL DETAILS</div>
                </div>
            </div>
            <div class="card-footer">
                <span>EMERGENCY MEDICAL CARD</span>
                <span>ID: ${cardData.profile_id.substring(0, 8)}</span>
            </div>
        </div>
    `;
    
    const cardDisplay = document.getElementById('emergencyCardDisplay');
    if (cardDisplay) {
        cardDisplay.innerHTML = cardHTML;
    }
}

// Download Card as Image
async function downloadCard() {
    try {
        showLoading();
        
        const cardElement = document.getElementById('downloadable-card');
        if (!cardElement) {
            showToast('No card to download', 'error');
            hideLoading();
            return;
        }
        
        // Load html2canvas if not already loaded
        if (!window.html2canvas) {
            await loadHtml2Canvas();
        }
        
        // Wait for QR image to load
        const qrImage = cardElement.querySelector('.barcode-image');
        if (qrImage && !qrImage.complete) {
            await new Promise(resolve => {
                qrImage.onload = resolve;
                qrImage.onerror = resolve;
            });
        }
        
        // Capture the card
        const canvas = await html2canvas(cardElement, {
            backgroundColor: null, // Transparent background
            scale: 3, // High quality
            logging: false,
            useCORS: true, // Allow cross-origin images
            allowTaint: true
        });
        
        // Convert to blob and download
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.download = `emergency-card-${new Date().getTime()}.png`;
            link.href = url;
            link.click();
            URL.revokeObjectURL(url);
            
            showToast('Card downloaded successfully!', 'success');
            hideLoading();
        }, 'image/png');
    } catch (error) {
        console.error('Error downloading card:', error);
        showToast('Error downloading card. Please try again.', 'error');
        hideLoading();
    }
}

// Load html2canvas library
function loadHtml2Canvas() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Handle Profile Submit
async function handleProfileSubmit(event) {
    event.preventDefault();
    showLoading();
    
    const profileData = {
        age: parseInt(document.getElementById('age').value) || null,
        gender: document.getElementById('gender').value || null,
        blood_group: document.getElementById('bloodGroup').value,
        height: document.getElementById('height').value || null,
        weight: document.getElementById('weight').value || null,
        address: document.getElementById('address').value || null,
        allergies: document.getElementById('allergies').value || null,
        medical_conditions: document.getElementById('medicalConditions').value || null,
        medications: document.getElementById('medications').value || null,
        medical_notes: document.getElementById('medicalNotes').value || null
    };
    
    try {
        const response = await fetch(`${API_URL}/api/profile?token=${authToken}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Profile saved! Emergency card generated.', 'success');
            
            // Update dashboard
            document.getElementById('bloodGroupDisplay').textContent = profileData.blood_group;
            
            // Reload card
            await loadEmergencyCard();
            
            // Switch to dashboard
            setTimeout(() => showSection('dashboard'), 1000);
        } else {
            showToast(data.detail || 'Failed to save profile', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Load Contacts
async function loadContacts() {
    try {
        const response = await fetch(`${API_URL}/api/contacts?token=${authToken}`);
        
        if (response.ok) {
            const data = await response.json();
            const contacts = data.contacts || [];
            
            const contactCountDisplay = document.getElementById('contactCountDisplay');
            if (contactCountDisplay) {
                contactCountDisplay.textContent = contacts.length;
            }
            
            const contactsList = document.getElementById('contactsList');
            if (!contactsList) return;
            
            if (contacts.length === 0) {
                contactsList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📞</div>
                        <div class="empty-state-text">No emergency contacts yet</div>
                        <div class="empty-state-subtext">Add contacts who should be notified in emergencies</div>
                    </div>
                `;
            } else {
                contactsList.innerHTML = contacts.map(contact => `
                    <div class="contact-card">
                        <div class="contact-header">
                            <div>
                                <div class="contact-name">${contact.name}</div>
                                <div class="contact-relation">${contact.relation}</div>
                            </div>
                            <button onclick="deleteContact('${contact.id}')" class="btn btn-danger">Delete</button>
                        </div>
                        <div class="contact-info">📱 ${contact.phone}</div>
                        ${contact.email ? `<div class="contact-info">✉️ ${contact.email}</div>` : ''}
                        <span class="priority-badge priority-${contact.priority}">
                            Priority ${contact.priority}
                        </span>
                    </div>
                `).join('');
                
                // Reload card to show updated contact
                await loadEmergencyCard();
            }
        }
    } catch (error) {
        console.error('Error loading contacts:', error);
    }
}

// Handle Contact Submit
async function handleContactSubmit(event) {
    event.preventDefault();
    showLoading();
    
    const contactData = {
        name: document.getElementById('contactName').value,
        relation: document.getElementById('contactRelation').value,
        phone: document.getElementById('contactPhone').value,
        email: document.getElementById('contactEmail').value || null,
        priority: parseInt(document.getElementById('contactPriority').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/api/contacts?token=${authToken}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contactData)
        });
        
        if (response.ok) {
            showToast('Contact added successfully!', 'success');
            event.target.reset();
            await loadContacts();
        } else {
            const data = await response.json();
            showToast(data.detail || 'Failed to add contact', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Delete Contact
async function deleteContact(contactId) {
    if (!confirm('Are you sure you want to delete this contact?')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_URL}/api/contacts/${contactId}?token=${authToken}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Contact deleted successfully!', 'success');
            await loadContacts();
        } else {
            showToast('Failed to delete contact', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Load Logs
async function loadLogs() {
    try {
        const response = await fetch(`${API_URL}/api/logs?token=${authToken}`);
        
        if (response.ok) {
            const data = await response.json();
            const logs = data.logs || [];
            
            const accessCountDisplay = document.getElementById('accessCountDisplay');
            if (accessCountDisplay) {
                accessCountDisplay.textContent = logs.length;
            }
            
            const logsList = document.getElementById('logsList');
            if (!logsList) return;
            
            if (logs.length === 0) {
                logsList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📊</div>
                        <div class="empty-state-text">No access logs yet</div>
                        <div class="empty-state-subtext">When you view your card, it will be logged here</div>
                    </div>
                `;
            } else {
                logsList.innerHTML = logs.map(log => {
                    const date = new Date(log.timestamp);
                    return `
                        <div class="log-item">
                            <div class="log-info">
                                <div class="log-type">${log.access_type}</div>
                                <div class="log-details">Accessed by: ${log.accessed_by}</div>
                            </div>
                            <div class="log-time">${date.toLocaleString()}</div>
                        </div>
                    `;
                }).join('');
            }
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Show Section
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
}

// Logout
function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    
    document.getElementById('authSection').style.display = 'flex';
    document.getElementById('appSection').style.display = 'none';
    document.getElementById('navbar').style.display = 'none';
    
    document.querySelectorAll('form').forEach(form => form.reset());
    
    showToast('Logged out successfully', 'success');
}
