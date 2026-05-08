/**
 * Native IndexedDB Wrapper for EduCore
 * No external libraries used.
 */

const DB_NAME = 'EduCoreOffline';
const DB_VERSION = 1;

class EduCoreDB {
    constructor(tenantPrefix) {
        this.prefix = tenantPrefix; // e.g. "greenwood"
        this.db = null;
    }

    async open() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                // List of stores to create. We use prefixes to support multiple schools in one browser.
                // In a real scenario, we might want to dynamically create stores based on the prefix.
                // But for this implementation, we'll assume a set of core stores.
                const stores = [
                    'students', 'teachers', 'academic_years', 'class_levels', 
                    'subjects', 'class_sections', 'attendance_sessions', 
                    'attendance_records', 'terms', 'grade_scales', 'results',
                    'announcements', 'sync_queue', 'meta',
                    'fee_structures', 'fee_invoices', 'fee_payments', 
                    'expense_categories', 'expenses'
                ];

                stores.forEach(storeName => {
                    // Store names are prefixed: greenwood_students
                    const prefixedName = `${this.prefix}_${storeName}`;
                    if (!db.objectStoreNames.contains(prefixedName)) {
                        db.createObjectStore(prefixedName, { keyPath: 'id' });
                    }
                });
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve(this.db);
            };

            request.onerror = (event) => reject(event.target.error);
        });
    }

    getStoreName(name) {
        return `${this.prefix}_${name}`;
    }

    async getAll(storeName) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.getStoreName(storeName)], 'readonly');
            const store = transaction.objectStore(this.getStoreName(storeName));
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getById(storeName, id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.getStoreName(storeName)], 'readonly');
            const store = transaction.objectStore(this.getStoreName(storeName));
            const request = store.get(id);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async put(storeName, data) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.getStoreName(storeName)], 'readwrite');
            const store = transaction.objectStore(this.getStoreName(storeName));
            const request = store.put(data);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async bulkPut(storeName, dataArray) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.getStoreName(storeName)], 'readwrite');
            const store = transaction.objectStore(this.getStoreName(storeName));
            dataArray.forEach(item => store.put(item));
            transaction.oncomplete = () => resolve();
            transaction.onerror = () => reject(transaction.error);
        });
    }

    async delete(storeName, id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.getStoreName(storeName)], 'readwrite');
            const store = transaction.objectStore(this.getStoreName(storeName));
            const request = store.delete(id);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async queueWrite(modelName, type, data) {
        const syncItem = {
            id: crypto.randomUUID(),
            model: modelName,
            type: type, // 'create', 'update', 'delete'
            data: data,
            timestamp: new Date().toISOString()
        };
        return this.put('sync_queue', syncItem);
    }

    async clearStore(storeName) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.getStoreName(storeName)], 'readwrite');
            const store = transaction.objectStore(this.getStoreName(storeName));
            const request = store.clear();
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
}

// Export for use in other scripts
window.EduCoreDB = EduCoreDB;
