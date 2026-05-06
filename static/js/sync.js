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
        
        // Initial check
        this.handleOnlineStatus(navigator.onLine);
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

        try {
            const response = await fetch('/api/sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ operations: queue })
            });

            if (response.ok) {
                const result = await response.json();
                // Clear the queue items that were successfully processed
                for (const res of result.results) {
                    if (res.status === 'success' || res.status === 'conflict') {
                        // Find the original queue item ID
                        const queueItem = queue.find(q => q.data.id === res.id);
                        if (queueItem) {
                            await this.db.delete('sync_queue', queueItem.id);
                        }
                        
                        if (res.status === 'conflict') {
                            console.warn("Conflict detected for", res.id, ". Server data wins.");
                            // Update local DB with server data
                            // Note: We need to know which store to update
                            // This would require more complex mapping
                        }
                    }
                }
                this.showSyncStatus('synced');
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
