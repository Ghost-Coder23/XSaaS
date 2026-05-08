/**
 * Sync Manager for EduCore
 * Handles connectivity detection and batch syncing.
 */

class SyncManager {
    constructor(db, tenantPrefix) {
        this.db = db;
        this.prefix = tenantPrefix;
        this.isSyncing = false;
        this.init();
    }

    init() {
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));
        
        // Intercept form submissions for offline use
        document.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Initial check
        this.handleOnlineStatus(navigator.onLine);
        this.updateOfflineOpsUI();
    }

    async updateOfflineOpsUI() {
        const sidebarBadge = document.getElementById('sync-sidebar-badge');
        const notifBadge = document.getElementById('notif-count');
        const syncPageList = document.getElementById('sync-page-list');
        
        const queue = await this.db.getAll('sync_queue');
        const count = queue.length;

        // 1. Update Sidebar Badge
        if (sidebarBadge) {
            if (count > 0) {
                sidebarBadge.innerText = count;
                sidebarBadge.classList.remove('d-none');
            } else {
                sidebarBadge.classList.add('d-none');
            }
        }

        // 2. Update Notification Tab Badge (Add count if pending)
        if (notifBadge) {
            // We only show the sync count if there are actually items in the queue
            if (count > 0) {
                // Get the base server notifications (ignoring the sync count we might have added previously)
                // We'll use a data attribute to store the real server count
                if (!notifBadge.hasAttribute('data-server-count')) {
                    notifBadge.setAttribute('data-server-count', notifBadge.innerText || '0');
                }
                const serverCount = parseInt(notifBadge.getAttribute('data-server-count')) || 0;
                
                notifBadge.innerText = serverCount + count;
                notifBadge.style.display = 'flex';
                notifBadge.title = `${count} pending offline actions`;
            } else if (notifBadge.hasAttribute('data-server-count')) {
                // Restore server count if queue is empty
                const serverCount = notifBadge.getAttribute('data-server-count');
                notifBadge.innerText = serverCount;
                if (parseInt(serverCount) === 0) {
                    notifBadge.style.display = 'none';
                }
            }
        }

        // 3. Update Sync Page List (if on that page)
        if (syncPageList) {
            if (count > 0) {
                syncPageList.innerHTML = queue.map(item => `
                    <tr>
                        <td>
                            <span class="badge bg-secondary text-uppercase" style="font-size: 0.65rem;">${item.type}</span>
                        </td>
                        <td class="fw-semibold">${item.model.replace('_', ' ')}</td>
                        <td class="text-muted small">${item.data._offline_origin || '/'}</td>
                        <td><span class="badge bg-warning text-dark"><i class="bi bi-clock me-1"></i>Pending</span></td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-outline-danger" onclick="syncManager.deleteFromQueue('${item.id}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            } else {
                syncPageList.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center py-5">
                            <div class="text-muted">
                                <i class="bi bi-check-circle-fill text-success fs-1 d-block mb-3"></i>
                                No pending offline actions.
                            </div>
                        </td>
                    </tr>
                `;
            }
        }
    }

    async deleteFromQueue(id) {
        if (confirm("Are you sure you want to discard this offline action?")) {
            await this.db.delete('sync_queue', id);
            this.updateOfflineOpsUI();
        }
    }

    /**
     * Optimistically update the local IndexedDB store
     * so that the UI shows the change immediately after navigation
     */
    async applyOptimisticUpdate(model, type, data) {
        const storeName = model + 's'; // e.g., 'students', 'fee_payments'
        try {
            if (type === 'delete') {
                // For delete, we don't actually delete from local DB yet (to allow undo/sync)
                // but we can mark it as hidden
                const existing = await this.db.get(storeName, data.id);
                if (existing) {
                    existing._offline_deleted = true;
                    await this.db.put(storeName, existing);
                }
            } else {
                // For create or update, merge the new data into the store
                const existing = await this.db.get(storeName, data.id) || {};
                const updated = { ...existing, ...data, _offline_pending: true };
                await this.db.put(storeName, updated);
            }
            console.log(`Optimistic ${type} applied to ${storeName}`);
        } catch (e) {
            console.warn("Optimistic update failed:", e);
        }
    }

    async handleFormSubmit(event) {
        const form = event.target;
        
        // Don't intercept logout or external forms
        if (form.action.includes('logout') || (form.action && !form.action.includes(window.location.origin) && form.action.startsWith('http'))) return;

        // Determine the model/action
        let modelName = form.getAttribute('data-offline-model');
        if (!modelName) {
            const path = window.location.pathname;
            if (path.includes('student')) modelName = 'student';
            else if (path.includes('teacher')) modelName = 'teacher';
            else if (path.includes('attendance')) modelName = 'attendance_record';
            else if (path.includes('payment') || path.includes('invoice')) modelName = 'fee_payment';
            else if (path.includes('user')) modelName = 'school_user';
            else modelName = 'generic_form';
        }

        // If we are definitely offline, handle immediately
        if (!navigator.onLine) {
            this.saveOffline(form, modelName, event);
            return;
        }

        // If we are "online", we still want to handle the case where the server is down
        // We do this by intercepting the submit and trying to fetch it ourselves
        event.preventDefault();
        
        const formData = new FormData(form);
        try {
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest', // Tell Django it's an AJAX request
                }
            });

            if (response.ok) {
                // Success! Redirect or reload as intended
                window.location.reload();
            } else {
                // Server returned an error (e.g. 500, 404)
                throw new Error("Server error");
            }
        } catch (error) {
            // Network error (Server down) or Server error
            console.log("Server unreachable or error, saving offline...");
            this.saveOffline(form, modelName);
        }
    }

    async saveOffline(form, modelName, event = null) {
        if (event) event.preventDefault();

        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            if (key === 'csrfmiddlewaretoken') return;
            data[key] = value;
        });

        // Determine operation type
        const isDelete = form.action.includes('delete') || form.querySelector('.btn-danger');
        const opType = isDelete ? 'delete' : (window.location.pathname.includes('add') || window.location.pathname.includes('create') ? 'create' : 'update');

        data.id = data.id || crypto.randomUUID();
        data._offline_origin = window.location.pathname;

        try {
            await this.db.queueWrite(modelName, opType, data);
            
            // OPTIMISTIC UPDATE: Update local IndexedDB so the change "appears" immediately
            await this.applyOptimisticUpdate(modelName, opType, data);
            
            this.updateOfflineOpsUI();
            
            // Show feedback
            const btn = form.querySelector('button[type="submit"]') || form.querySelector('button');
            if (btn) {
                btn.innerHTML = '<i class="bi bi-cloud-check"></i> Saved Offline';
                btn.classList.add('btn-warning');
                btn.disabled = true;
            }

            const alert = document.createElement('div');
            alert.className = 'alert alert-warning mt-3 shadow-sm border-0';
            alert.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-info-circle-fill fs-4 me-3"></i>
                    <div>
                        <strong>Action Saved Offline!</strong><br>
                        The server is currently unreachable. Your changes have been stored locally and will sync automatically.
                    </div>
                </div>
            `;
            form.prepend(alert);

            setTimeout(() => {
                const backBtn = document.querySelector('a.btn-secondary') || document.querySelector('.btn-back');
                window.location.href = (backBtn && backBtn.href) ? backBtn.href : '/analytics/dashboard/';
            }, 2500);
        } catch (e) {
            console.error("Failed to save offline:", e);
        }
    }

    handleOnlineStatus(isOnline) {
        const banner = document.getElementById('offline-banner');
        if (!isOnline) {
            if (banner) banner.style.display = 'block';
            console.log("App is offline. Changes will be saved locally.");
        } else {
            if (banner) banner.style.display = 'none';
            console.log("App is online. Starting sync...");
            this.flushQueue();
        }
    }

    async flushQueue() {
        if (this.isSyncing || !navigator.onLine) return;
        
        const queue = await this.db.getAll('sync_queue');
        if (queue.length === 0) return;

        this.isSyncing = true;
        this.showSyncStatus('syncing');

        // Prepare operations with model name included
        const operations = queue.map(item => ({
            model: item.model,
            type: item.type,
            data: item.data
        }));

        try {
            const response = await fetch('/api/sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ operations: operations })
            });

            if (response.ok) {
                const result = await response.json();
                // Clear the queue items that were successfully processed
                for (const res of result.results) {
                    if (res.status === 'success' || res.status === 'conflict') {
                        // Find the original queue item
                        const queueItem = queue.find(q => q.data.id === res.id);
                        if (queueItem) {
                            // Find the internal IndexedDB ID for deletion
                            const internalItem = (await this.db.getAll('sync_queue')).find(i => i.data.id === res.id);
                            if (internalItem) {
                                await this.db.delete('sync_queue', internalItem.id);
                            }
                            
                            // If it was a create/update, update local store with server's confirmed data
                            if (res.data) {
                                await this.db.put(queueItem.model + 's', res.data);
                            }
                        }
                        
                        if (res.status === 'conflict') {
                            console.warn("Conflict detected for", res.id, ". Server data wins.");
                        }
                    }
                }
                this.showSyncStatus('synced');
                this.updateOfflineOpsUI();
            } else {
                this.showSyncStatus('failed');
            }
        } catch (error) {
            console.error("Sync failed:", error);
            this.showSyncStatus('failed');
        } finally {
            this.isSyncing = false;
        }
    }

    showSyncStatus(status) {
        const indicator = document.getElementById('sync-indicator');
        if (!indicator) return;

        indicator.className = 'sync-status';
        indicator.style.display = 'block';

        switch (status) {
            case 'syncing':
                indicator.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Syncing...';
                indicator.classList.add('bg-info');
                break;
            case 'synced':
                indicator.innerHTML = '<i class="bi bi-check-circle"></i> All data synced';
                indicator.classList.add('bg-success');
                setTimeout(() => indicator.style.display = 'none', 3000);
                break;
            case 'failed':
                indicator.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Sync failed. <button onclick="syncManager.flushQueue()">Retry</button>';
                indicator.classList.add('bg-danger');
                break;
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async initialSync() {
        if (!navigator.onLine) return;
        
        try {
            const response = await fetch('/api/initial-sync/');
            if (response.ok) {
                const data = await response.json();
                
                // Bulk save all data to IndexedDB
                for (const [key, value] of Object.entries(data)) {
                    if (Array.isArray(value)) {
                        await this.db.bulkPut(key, value);
                    } else if (key === 'school') {
                        await this.db.put('meta', { id: 'current_school', ...value });
                    }
                }
                console.log("Initial sync completed.");
            }
        } catch (error) {
            console.error("Initial sync failed:", error);
        }
    }
}

window.SyncManager = SyncManager;
