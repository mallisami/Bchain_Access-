/**
 * frontend_integration.js
 * Healthcare Blockchain Access Control - Frontend Integration Layer
 *
 * This module replaces the existing prototype's pure client-side state management
 * with API calls to the Flask backend. It maintains all existing accessibility
 * features (ARIA live regions, keyboard navigation, screen reader announcements)
 * while adding blockchain-aware functionality:
 *
 * - API client for all backend endpoints
 * - Blockchain status polling and WebSocket fallback
 * - Transaction hash display and blockchain explorer links
 * - Proper error handling with user-friendly messages
 * - Session management with automatic timeout warnings
 *
 * Usage: Include this file after the existing HTML prototype's inline script,
 * or import it as a module. It wraps and replaces the key functions from the
 * original prototype.
 *
 * @version 1.0.0
 */

(function () {
  "use strict";

  // =========================================================================
  // CONFIGURATION
  // =========================================================================

  const CONFIG = {
    API_BASE_URL: "http://localhost:5000/api",
    POLL_INTERVAL_MS: 5000,        // Blockchain status polling interval
    SESSION_WARNING_MS: 2 * 60 * 1000, // Warn 2 minutes before expiry (matches prototype)
    FETCH_TIMEOUT_MS: 10000,       // API request timeout
    MAX_RETRIES: 2,                // Retry failed requests
    PENDING_COUNTDOWN_SECONDS: 60, // Must match backend and smart contract
  };

  // =========================================================================
  // STATE
  // =========================================================================

  const state = {
    session: {
      active: false,
      startedAt: null,
      expiresAt: null,
    },
    blockchain: {
      connected: false,
      latestBlock: null,
      chainId: null,
    },
    pollIntervalId: null,
    pendingGrant: null,
    countdownIntervalId: null,
  };

  // =========================================================================
  // UTILITY FUNCTIONS
  // =========================================================================

  /**
   * Make an API request with timeout, retries, and error handling.
   */
  async function apiRequest(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.FETCH_TIMEOUT_MS);

    let lastError;
    for (let attempt = 0; attempt <= CONFIG.MAX_RETRIES; attempt++) {
      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            ...(options.headers || {}),
          },
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new ApiError(
            errorData.error || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData
          );
        }
        return await response.json();
      } catch (error) {
        lastError = error;
        if (error.name === "AbortError") {
          console.warn(`API request timed out: ${url}`);
        } else if (attempt < CONFIG.MAX_RETRIES) {
          await sleep(1000 * (attempt + 1)); // Exponential backoff
        }
      }
    }

    clearTimeout(timeoutId);
    throw lastError;
  }

  class ApiError extends Error {
    constructor(message, statusCode, data) {
      super(message);
      this.name = "ApiError";
      this.statusCode = statusCode;
      this.data = data;
    }
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function formatTimestamp(isoString) {
    if (!isoString) return "N/A";
    const date = new Date(isoString);
    return date.toLocaleString();
  }

  function formatAddress(address) {
    if (!address || address.length < 12) return address;
    return `${address.slice(0, 8)}...${address.slice(-6)}`;
  }

  // =========================================================================
  // ARIA / ACCESSIBILITY HELPERS (preserve existing prototype behavior)
  // =========================================================================

  function announceToScreenReader(message) {
    const region = document.getElementById("status-region");
    if (!region) return;
    setTimeout(() => {
      region.textContent = "";
      setTimeout(() => {
        region.textContent = message;
      }, 100);
    }, 100);
  }

  function announceAssertive(message) {
    const region = document.getElementById("sr-status");
    if (!region) return;
    setTimeout(() => {
      region.textContent = "";
      setTimeout(() => {
        region.textContent = message;
      }, 100);
    }, 100);
  }

  // =========================================================================
  // API CLIENT - AUTHENTICATION
  // =========================================================================

  async function apiAuthUnlock(method = "fingerprint") {
    return apiRequest("/auth/unlock", {
      method: "POST",
      body: JSON.stringify({ method }),
    });
  }

  async function apiAuthStatus() {
    return apiRequest("/auth/status");
  }

  async function apiAuthExtend() {
    return apiRequest("/auth/extend", { method: "POST" });
  }

  // =========================================================================
  // API CLIENT - RECORDS
  // =========================================================================

  async function apiGetRecords() {
    return apiRequest("/records");
  }

  async function apiGetRecord(recordId) {
    return apiRequest(`/records/${encodeURIComponent(recordId)}`);
  }

  // =========================================================================
  // API CLIENT - ACCESS CONTROL
  // =========================================================================

  async function apiGrantAccess(providerId, recordIds, accessLevel = 1, expirationDays = 0) {
    return apiRequest("/access/grant", {
      method: "POST",
      body: JSON.stringify({ provider_id: providerId, record_ids: recordIds, access_level: accessLevel, expiration_days: expirationDays }),
    });
  }

  async function apiConfirmAccess(pendingId) {
    return apiRequest("/access/confirm", {
      method: "POST",
      body: JSON.stringify({ pending_id: pendingId }),
    });
  }

  async function apiCancelAccess(pendingId) {
    return apiRequest("/access/cancel", {
      method: "POST",
      body: JSON.stringify({ pending_id: pendingId }),
    });
  }

  async function apiRevokeAccess(providerId, recordId) {
    return apiRequest("/access/revoke", {
      method: "POST",
      body: JSON.stringify({ provider_id: providerId, record_id: recordId }),
    });
  }

  async function apiCheckAccess(providerId, recordId) {
    return apiRequest(`/access/check?provider_id=${encodeURIComponent(providerId)}&record_id=${encodeURIComponent(recordId)}`);
  }

  async function apiGetPendingGrants() {
    return apiRequest("/access/pending");
  }

  // =========================================================================
  // API CLIENT - AUDIT
  // =========================================================================

  async function apiGetAuditLog(recordId) {
    return apiRequest(`/audit/log?record_id=${encodeURIComponent(recordId)}`);
  }

  // =========================================================================
  // API CLIENT - BLOCKCHAIN
  // =========================================================================

  async function apiBlockchainStatus() {
    return apiRequest("/blockchain/status");
  }

  async function apiBlockchainExplorer(page = 1, perPage = 10) {
    return apiRequest(`/blockchain/explorer?page=${page}&per_page=${perPage}`);
  }

  async function apiBlockchainVerify() {
    return apiRequest("/blockchain/verify");
  }

  // =========================================================================
  // UI UPDATE HELPERS
  // =========================================================================

  function setButtonLoading(button, loading = true) {
    if (!button) return;
    button.disabled = loading;
    button.setAttribute("aria-busy", loading ? "true" : "false");
  }

  function showBlockchainStatusBanner(status) {
    let banner = document.getElementById("blockchain-status-banner");
    if (!banner) {
      banner = document.createElement("div");
      banner.id = "blockchain-status-banner";
      banner.className = "status-banner";
      banner.setAttribute("role", "status");
      banner.setAttribute("aria-live", "polite");
      banner.setAttribute("aria-atomic", "true");
      const header = document.querySelector(".site-header");
      if (header) header.insertAdjacentElement("afterend", banner);
    }

    if (status.connected) {
      banner.className = "status-banner status-banner--success";
      banner.innerHTML = `<p><strong>Blockchain connected.</strong> Network: ${status.network} | Chain ID: ${status.chain_id} | Latest block: #${status.latest_block.index} | ${status.mempool.size} pending transactions</p>`;
    } else {
      banner.className = "status-banner status-banner--error";
      banner.innerHTML = `<p><strong>Blockchain disconnected.</strong> Some features may be unavailable.</p>`;
    }
  }

  function displayTransactionHash(txHash, containerId = "tx-display") {
    let container = document.getElementById(containerId);
    if (!container) {
      container = document.createElement("div");
      container.id = containerId;
      container.className = "mt-md";
    }
    container.innerHTML = `
      <p style="font-size: 0.9rem; color: var(--text-muted);">
        <strong>Transaction:</strong>
        <a href="${CONFIG.API_BASE_URL}/blockchain/transaction/${encodeURIComponent(txHash)}" 
           target="_blank" rel="noopener noreferrer"
           style="font-family: monospace; word-break: break-all;"
           aria-label="View transaction ${formatAddress(txHash)} on blockchain explorer">
          ${txHash}
        </a>
        <span class="tooltip-trigger" tabindex="0" aria-describedby="tx-tooltip">
          <span class="tooltip-icon" aria-hidden="true">?</span>
          <span class="sr-only">What is a transaction hash?</span>
          <span class="tooltip-content" id="tx-tooltip" role="tooltip">
            A transaction hash identifies this ledger action. In the local-EVM mode it can be used to inspect the development-chain transaction; fallback-mode identifiers are simulated.
          </span>
        </span>
      </p>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
        <a href="${CONFIG.API_BASE_URL}/blockchain/explorer" target="_blank" rel="noopener noreferrer" style="text-decoration: underline;">
          Open Blockchain Explorer
        </a> to see all confirmed transactions.
      </p>
    `;
    return container;
  }

  function showError(message, containerId = "error-display") {
    let container = document.getElementById(containerId);
    if (!container) {
      container = document.createElement("div");
      container.id = containerId;
      container.className = "status-banner status-banner--error";
      container.setAttribute("role", "alert");
      container.setAttribute("aria-live", "assertive");
      const main = document.querySelector("main");
      if (main) main.insertBefore(container, main.firstChild);
    }
    container.className = "status-banner status-banner--error";
    container.innerHTML = `<p><strong>Error:</strong> ${message}</p>`;
    container.style.display = "block";
    announceAssertive(`Error: ${message}`);
  }

  function hideError(containerId = "error-display") {
    const container = document.getElementById(containerId);
    if (container) container.style.display = "none";
  }

  // =========================================================================
  // BLOCKCHAIN STATUS POLLING
  // =========================================================================

  async function pollBlockchainStatus() {
    try {
      const status = await apiBlockchainStatus();
      state.blockchain.connected = status.connected;
      state.blockchain.latestBlock = status.latest_block;
      state.blockchain.chainId = status.chain_id;
      showBlockchainStatusBanner(status);
    } catch (error) {
      console.warn("Blockchain polling failed:", error);
      state.blockchain.connected = false;
      showBlockchainStatusBanner({ connected: false });
    }
  }

  function startBlockchainPolling() {
    if (state.pollIntervalId) clearInterval(state.pollIntervalId);
    pollBlockchainStatus(); // Immediate first poll
    state.pollIntervalId = setInterval(pollBlockchainStatus, CONFIG.POLL_INTERVAL_MS);
  }

  function stopBlockchainPolling() {
    if (state.pollIntervalId) {
      clearInterval(state.pollIntervalId);
      state.pollIntervalId = null;
    }
  }

  // =========================================================================
  // REPLACED FUNCTIONS (override prototype functions)
  // =========================================================================

  // Override the original unlockSession to call the backend
  window.unlockSession = async function () {
    const btn = document.getElementById("fingerprint-btn");
    setButtonLoading(btn, true);
    hideError();

    try {
      const result = await apiAuthUnlock("fingerprint");
      state.session.active = true;
      state.session.startedAt = new Date(result.session.started_at);
      state.session.expiresAt = new Date(result.session.expires_at);

      document.getElementById("auth-locked").classList.add("hidden");
      document.getElementById("auth-unlocked").classList.remove("hidden");
      document.getElementById("dashboard-section").classList.remove("hidden");
      document.getElementById("grant-section").classList.remove("hidden");
      document.getElementById("help-section").classList.remove("hidden");

      // Show blockchain info in the success banner
      const successBanner = document.querySelector("#auth-unlocked .status-banner");
      if (successBanner) {
        successBanner.innerHTML = `
          <p><strong>Session secured.</strong> Your records are protected on the blockchain.</p>
          <p style="margin-top: 4px; font-size: 0.9rem;">
            Blockchain TX: <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 4px;">${formatAddress(result.blockchain.tx_hash)}</code>
            | Block #${result.blockchain.block_number}
            | Gas used: ${result.blockchain.gas_used}
          </p>
        `;
      }

      announceAssertive("Session secured on blockchain. Your records are now available.");
      document.getElementById("auth-unlocked").querySelector(".status-banner").setAttribute("tabindex", "-1");
      document.getElementById("auth-unlocked").querySelector(".status-banner").focus();

      // Start blockchain polling
      startBlockchainPolling();

      // Load records from backend
      await loadRecordsFromBackend();

      // Start session timer
      startSessionTimer();
    } catch (error) {
      console.error("Unlock failed:", error);
      showError(
        error instanceof ApiError
          ? error.message
          : "Could not unlock your session. Please check your connection and try again."
      );
    } finally {
      setButtonLoading(btn, false);
    }
  };

  // Load records from backend and update the dashboard
  async function loadRecordsFromBackend() {
    try {
      const result = await apiGetRecords();
      const records = result.records;
      updateDashboard(records);
    } catch (error) {
      console.error("Failed to load records:", error);
      showError("Could not load your records from the blockchain. Please refresh the page.");
    }
  }

  function updateDashboard(records) {
    // Find the dashboard panel
    const panel = document.getElementById("dashboard-panel");
    if (!panel) return;

    // Keep the system status banner, rebuild the rest
    let html = `
      <div class="status-banner status-banner--info" role="status" aria-live="polite">
        <p id="system-status"><strong>Your records are secured on the blockchain.</strong> Waiting for your confirmation to share access.</p>
      </div>
    `;

    records.forEach((record) => {
      const activeGrants = record.access_grants || [];
      const isPrivate = activeGrants.length === 0;
      const statusClass = isPrivate ? "access-badge--none" : "access-badge--active";
      const statusText = isPrivate ? "Private" : "Active";

      html += `
        <div class="record-card" data-record-id="${record.record_id}">
          <div class="record-card__header">
            <div>
              <h3 id="record-${record.record_id}-title">${record.record_type}</h3>
              <p class="record-card__meta">Date: ${record.date} | Facility: ${record.facility}</p>
              <p class="record-card__meta" style="font-family: monospace; font-size: 0.8rem;">
                Record Hash: ${formatAddress(record.record_hash)}
              </p>
            </div>
            <span class="access-badge ${statusClass}">${statusText}</span>
          </div>
      `;

      if (activeGrants.length > 0) {
        html += `<h4 id="access-heading-${record.record_id}">Who can see this record:</h4>`;
        html += `<ul class="access-list" aria-labelledby="access-heading-${record.record_id}">`;
        activeGrants.forEach((grant) => {
          html += `
            <li class="access-list__item">
              <div>
                <strong>${grant.provider_name}</strong> — ${grant.provider_specialty}
                <span class="access-badge access-badge--active" style="margin-left: var(--space-sm);">Active Access</span>
                <br>
                <span style="font-size: 0.875rem; color: var(--text-muted);">
                  Granted: ${new Date(grant.grant_timestamp * 1000).toLocaleDateString()}
                  | TX: <a href="${CONFIG.API_BASE_URL}/blockchain/transaction/${encodeURIComponent(grant.tx_hash)}" target="_blank" rel="noopener noreferrer" style="font-family: monospace;">${formatAddress(grant.tx_hash)}</a>
                </span>
              </div>
              <button
                class="btn btn--danger"
                onclick="revokeAccess('${grant.provider_id}', '${record.record_id}')"
                aria-label="Remove access for ${grant.provider_name} to view your ${record.record_type}"
                type="button"
              >
                Remove Access
              </button>
            </li>
          `;
        });
        html += `</ul>`;

        // Add audit log link
        html += `
          <p style="margin-top: var(--space-md); font-size: 0.9rem;">
            <a href="javascript:void(0)" onclick="showAuditLog('${record.record_id}')" style="color: var(--primary); text-decoration: underline;">
              View audit log for this record
            </a>
          </p>
        `;
      } else {
        html += `<p style="color: var(--text-muted); font-size: 0.95rem;">No one has access to this record. Only you can see it.</p>`;
      }

      html += `</div>`;
    });

    panel.innerHTML = html;
  }

  // Override revokeAccess to call the backend
  window.revokeAccess = async function (providerId, recordId) {
    const providerNames = {
      "dr-sarah-chen": "Dr. Sarah Chen",
      "dr-michael-torres": "Dr. Michael Torres",
      "dr-james-wilson": "Dr. James Wilson",
      "metro-physical-therapy": "Metro Physical Therapy",
    };
    const providerName = providerNames[providerId] || providerId;

    if (!confirm(`Are you sure you want to remove ${providerName}'s access to this record? They will no longer be able to view it. This action will be recorded on the blockchain.`)) {
      announceToScreenReader("Access removal cancelled. No changes were made.");
      return;
    }

    try {
      const result = await apiRevokeAccess(providerId, recordId);

      announceAssertive(`${providerName}'s access has been removed. Transaction recorded on blockchain.`);
      showError(`${result.message} Transaction: ${formatAddress(result.tx_hash)}`, "success-display");
      const successDiv = document.getElementById("success-display");
      if (successDiv) successDiv.className = "status-banner status-banner--success";

      // Refresh the dashboard
      await loadRecordsFromBackend();
    } catch (error) {
      console.error("Revoke failed:", error);
      showError(
        error instanceof ApiError
          ? error.message
          : "Could not remove access. Please try again."
      );
    }
  };

  // Override proceedToReview to gather selections and prepare
  window.proceedToReview = async function () {
    const providerSelect = document.getElementById("provider-select");
    const providerValue = providerSelect.value;
    const [providerId, providerName, providerSpecialty] = providerValue.split("|");

    const recordCheckboxes = document.querySelectorAll('input[name="records"]:checked');
    if (recordCheckboxes.length === 0) {
      announceAssertive("Please select at least one record to share. Use the checkboxes to choose which records you want to share.");
      document.querySelector('input[name="records"]').focus();
      return;
    }

    window.selectedProviderName = providerName;
    window.selectedProviderSpecialty = providerSpecialty;
    window.selectedProviderId = providerId;
    window.selectedRecordIds = Array.from(recordCheckboxes).map((cb) => cb.value.split("|")[1]);
    window.selectedRecordsList = Array.from(recordCheckboxes).map((cb) => cb.value.split("|")[0]);

    document.getElementById("review-records").textContent = window.selectedRecordsList.join(", ");
    document.getElementById("review-provider").textContent = providerName + ", " + providerSpecialty;

    const consequenceEl = document.querySelector(".consequence-statement p");
    const recordsText =
      window.selectedRecordsList.length > 1
        ? window.selectedRecordsList.join(", ") + " records"
        : window.selectedRecordsList[0];
    consequenceEl.innerHTML = `<strong>What this means:</strong> ${providerName} will receive view-only authorization for your ${recordsText} in this demonstration. You can remove that authorization at any time. The action will receive a local-EVM transaction hash or a simulated fallback-ledger identifier.`;

    document.getElementById("grant-stage-1").classList.add("hidden");
    document.getElementById("grant-stage-2").classList.remove("hidden");

    document.getElementById("step-1-indicator").className = "step step--complete";
    document.getElementById("step-1-indicator").innerHTML = '<span class="sr-only">Completed step: </span>1. Select &#10003;';
    document.getElementById("step-2-indicator").className = "step step--current";
    document.getElementById("step-2-indicator").innerHTML = '<span class="sr-only">Current step: </span>2. Review';

    announceToScreenReader(`Step 2: Review. You are about to let ${providerName} view ${window.selectedRecordsList.join(", ")}. They can view only and cannot edit or download your records. This will be recorded on the blockchain.`);
    document.getElementById("review-heading").setAttribute("tabindex", "-1");
    document.getElementById("review-heading").focus();
  };

  // Override proceedToConfirm to call the backend
  window.proceedToConfirm = async function () {
    const btn = document.getElementById("btn-confirm");
    setButtonLoading(btn, true);
    hideError();

    try {
      const result = await apiGrantAccess(
        window.selectedProviderId,
        window.selectedRecordIds,
        1, // VIEW_ONLY
        0  // No expiration
      );

      state.pendingGrant = result;

      document.getElementById("grant-stage-2").classList.add("hidden");
      document.getElementById("grant-stage-3").classList.remove("hidden");

      document.getElementById("step-2-indicator").className = "step step--complete";
      document.getElementById("step-2-indicator").innerHTML = '<span class="sr-only">Completed step: </span>2. Review &#10003;';
      document.getElementById("step-3-indicator").className = "step step--current";
      document.getElementById("step-3-indicator").innerHTML = '<span class="sr-only">Current step: </span>3. Confirm';

      // The contract enforces a minimum waiting period. Confirmation becomes
      // available when the countdown reaches zero; the request does not expire.
      let countdownSeconds = result.countdown_seconds || 60;
      const confirmButton = document.getElementById("btn-final-confirm");
      if (confirmButton) confirmButton.disabled = true;
      updateCountdownDisplay(countdownSeconds);
      if (state.countdownIntervalId) clearInterval(state.countdownIntervalId);
      state.countdownIntervalId = setInterval(() => {
        countdownSeconds--;
        updateCountdownDisplay(countdownSeconds);
        if (countdownSeconds <= 0) {
          clearInterval(state.countdownIntervalId);
          updateCountdownDisplay(0);
          if (confirmButton) {
            confirmButton.disabled = false;
            confirmButton.focus();
          }
          announceAssertive("Confirmation is now available. Choose Confirm Grant Access to finalize, or Cancel to stop.");
        }
      }, 1000);

      // Show transaction hash
      const txContainer = displayTransactionHash(result.tx_hashes[0], "grant-tx-display");
      const stage3 = document.getElementById("grant-stage-3");
      if (stage3 && txContainer) {
        stage3.insertBefore(txContainer, stage3.querySelector(".flex-wrap"));
      }

      announceToScreenReader(`Step 3 of 3: Confirm. Confirmation will be available in ${countdownSeconds} seconds for ${window.selectedProviderName}. You may cancel at any time before confirming.`);
    } catch (error) {
      console.error("Grant initiation failed:", error);
      showError(
        error instanceof ApiError
          ? error.message
          : "Could not initiate access grant. Please try again."
      );
    } finally {
      setButtonLoading(btn, false);
    }
  };

  function updateCountdownDisplay(seconds) {
    const numEl = document.getElementById("countdown-number");
    if (numEl) numEl.textContent = seconds > 0 ? seconds : "Ready";
    const labelEl = document.getElementById("countdown-label");
    if (labelEl && seconds <= 0) labelEl.textContent = "Confirmation is now available";
    if (seconds % 10 === 0 || (seconds <= 5 && seconds > 0)) {
      const pendingStatus = document.getElementById("pending-status");
      if (pendingStatus) {
        pendingStatus.textContent = seconds > 0
          ? `Confirmation will be available in ${seconds} seconds. You may cancel before confirming.`
          : "Confirmation is now available. You may confirm or cancel.";
      }
    }
  }

  // Override finalConfirm to call the backend
  window.finalConfirm = async function () {
    if (!state.pendingGrant || !state.pendingGrant.pending_id) {
      showError("No pending grant found. Please start over.");
      return;
    }

    const btn = document.getElementById("btn-final-confirm");
    setButtonLoading(btn, true);
    hideError();

    try {
      const result = await apiConfirmAccess(state.pendingGrant.pending_id);

      if (state.countdownIntervalId) clearInterval(state.countdownIntervalId);

      document.getElementById("grant-stage-3").classList.add("hidden");
      document.getElementById("grant-success").classList.remove("hidden");

      document.getElementById("step-3-indicator").className = "step step--complete";
      document.getElementById("step-3-indicator").innerHTML = '<span class="sr-only">Completed step: </span>3. Confirm &#10003;';

      document.getElementById("system-status").innerHTML = `<strong>Access updated on blockchain.</strong> ${window.selectedProviderName} now has view access to your records.`;

      // Show success transaction info
      const successDiv = document.getElementById("grant-success");
      const txContainer = displayTransactionHash(result.tx_hashes[0], "confirm-tx-display");
      if (successDiv && txContainer && !document.getElementById("confirm-tx-display")) {
        successDiv.appendChild(txContainer);
      }

      announceAssertive(`Access granted successfully on blockchain. ${window.selectedProviderName} can now view your ${window.selectedRecordsList.join(", ")}. You can remove this access at any time.`);
      successDiv.querySelector(".status-banner").setAttribute("tabindex", "-1");
      successDiv.querySelector(".status-banner").focus();

      // Refresh dashboard
      await loadRecordsFromBackend();
    } catch (error) {
      console.error("Confirmation failed:", error);
      if (error instanceof ApiError && error.statusCode === 400) {
        showError(error.message || "Still in pending period. Please wait for the countdown to complete.");
      } else {
        showError(
          error instanceof ApiError
            ? error.message
            : "Could not confirm access grant. Please try again."
        );
      }
    } finally {
      setButtonLoading(btn, false);
    }
  };

  // Override cancelGrant to call the backend
  window.cancelGrant = async function () {
    if (state.countdownIntervalId) clearInterval(state.countdownIntervalId);

    if (state.pendingGrant && state.pendingGrant.pending_id) {
      try {
        await apiCancelAccess(state.pendingGrant.pending_id);
      } catch (error) {
        console.warn("Backend cancel failed (may be already expired):", error);
      }
    }

    document.getElementById("grant-stage-3").classList.add("hidden");
    document.getElementById("grant-stage-1").classList.remove("hidden");

    document.getElementById("step-1-indicator").className = "step step--current";
    document.getElementById("step-1-indicator").innerHTML = '<span class="sr-only">Current step: </span>1. Select';
    document.getElementById("step-2-indicator").className = "step step--pending";
    document.getElementById("step-2-indicator").innerHTML = '<span class="sr-only">Pending step: </span>2. Review';
    document.getElementById("step-3-indicator").className = "step step--pending";
    document.getElementById("step-3-indicator").innerHTML = '<span class="sr-only">Pending step: </span>3. Confirm';

    document.getElementById("btn-final-confirm").disabled = false;
    state.pendingGrant = null;

    // Remove any transaction displays
    ["grant-tx-display", "confirm-tx-display"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.remove();
    });

    announceToScreenReader("Access request cancelled on blockchain. No changes were made. You can start over if you want to grant access.");
    document.getElementById("provider-select").focus();
  };

  // Override resetGrantWorkflow
  window.resetGrantWorkflow = function () {
    document.getElementById("grant-success").classList.add("hidden");
    document.getElementById("grant-stage-1").classList.remove("hidden");

    document.getElementById("step-1-indicator").className = "step step--current";
    document.getElementById("step-1-indicator").innerHTML = '<span class="sr-only">Current step: </span>1. Select';
    document.getElementById("step-2-indicator").className = "step step--pending";
    document.getElementById("step-2-indicator").innerHTML = '<span class="sr-only">Pending step: </span>2. Review';
    document.getElementById("step-3-indicator").className = "step step--pending";
    document.getElementById("step-3-indicator").innerHTML = '<span class="sr-only">Pending step: </span>3. Confirm';

    document.querySelectorAll('input[name="records"]').forEach((cb) => (cb.checked = false));
    document.getElementById("record-mri").checked = true;

    state.pendingGrant = null;

    // Remove any transaction displays
    ["grant-tx-display", "confirm-tx-display"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.remove();
    });

    announceToScreenReader("Grant access workflow reset. Step 1: Select a provider and records.");
    document.getElementById("provider-select").focus();
  };

  // Override goBackToSelection
  window.goBackToSelection = function () {
    document.getElementById("grant-stage-2").classList.add("hidden");
    document.getElementById("grant-stage-1").classList.remove("hidden");

    document.getElementById("step-1-indicator").className = "step step--current";
    document.getElementById("step-1-indicator").innerHTML = '<span class="sr-only">Current step: </span>1. Select';
    document.getElementById("step-2-indicator").className = "step step--pending";
    document.getElementById("step-2-indicator").innerHTML = '<span class="sr-only">Pending step: </span>2. Review';

    announceToScreenReader("Returned to step 1: Select. You can change your provider or records.");
    document.getElementById("provider-select").focus();
  };

  // =========================================================================
  // NEW FEATURE: AUDIT LOG VIEWER
  // =========================================================================

  window.showAuditLog = async function (recordId) {
    try {
      const result = await apiGetAuditLog(recordId);
      const modal = createModal("Audit Log", `
        <div style="max-height: 400px; overflow-y: auto;">
          <p style="margin-bottom: var(--space-md);">
            <strong>Record:</strong> ${result.record_id}<br>
            <strong>Hash:</strong> <code style="font-size: 0.8rem;">${result.record_hash}</code>
          </p>
          <h4 style="margin-bottom: var(--space-sm);">Blockchain Events</h4>
          <ul style="list-style: none; padding: 0;">
            ${result.blockchain_events.map((e) => `
              <li style="padding: var(--space-sm); border-bottom: 1px solid #e0e0e0; font-size: 0.9rem;">
                <strong>${e.action}</strong> — ${new Date(e.timestamp * 1000).toLocaleString()}<br>
                Block #${e.block_number} | TX: <code>${formatAddress(e.tx_hash)}</code><br>
                From: ${formatAddress(e.from)} | Gas: ${e.gas_used}
              </li>
            `).join("")}
          </ul>
          <h4 style="margin: var(--space-lg) 0 var(--space-sm);">Application Events</h4>
          <ul style="list-style: none; padding: 0;">
            ${result.audit_entries.map((e) => `
              <li style="padding: var(--space-sm); border-bottom: 1px solid #e0e0e0; font-size: 0.9rem;">
                <strong>${e.action}</strong> — ${new Date(e.timestamp * 1000).toLocaleString()}<br>
                ${e.details || ""}
              </li>
            `).join("")}
          </ul>
        </div>
      `);
      document.body.appendChild(modal);
      modal.querySelector(".modal-close").focus();
    } catch (error) {
      console.error("Failed to load audit log:", error);
      showError("Could not load the audit log. Please try again.");
    }
  };

  function createModal(title, content) {
    const overlay = document.createElement("div");
    overlay.style.cssText = "position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: var(--space-md);";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-labelledby", "modal-title");

    overlay.innerHTML = `
      <div style="background: white; border-radius: 8px; max-width: 600px; width: 100%; max-height: 80vh; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.2);" role="document">
        <div style="padding: var(--space-lg); border-bottom: 1px solid #e0e0e0; display: flex; justify-content: space-between; align-items: center;">
          <h3 id="modal-title" style="margin: 0; color: var(--primary);">${title}</h3>
          <button class="modal-close btn btn--cancel" style="min-height: 36px; padding: var(--space-xs) var(--space-md);" aria-label="Close audit log dialog">Close</button>
        </div>
        <div style="padding: var(--space-lg);">${content}</div>
      </div>
    `;

    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) overlay.remove();
    });
    overlay.querySelector(".modal-close").addEventListener("click", () => overlay.remove());
    overlay.addEventListener("keydown", (e) => {
      if (e.key === "Escape") overlay.remove();
    });

    return overlay;
  }

  // =========================================================================
  // SESSION MANAGEMENT (with backend sync)
  // =========================================================================

  let sessionTimerId;
  let sessionWarningShown = false;

  function startSessionTimer() {
    sessionWarningShown = false;
    if (sessionTimerId) clearInterval(sessionTimerId);

    sessionTimerId = setInterval(async () => {
      try {
        const status = await apiAuthStatus();
        if (!status.active) {
          expireSession();
          return;
        }

        const remaining = status.remaining_seconds;
        if (!sessionWarningShown && remaining <= 120 && remaining > 0) {
          showTimeoutWarning();
          sessionWarningShown = true;
        }
      } catch (error) {
        console.warn("Session sync failed:", error);
      }
    }, 30000); // Check every 30 seconds
  }

  function showTimeoutWarning() {
    const bar = document.getElementById("timeout-bar");
    if (bar) bar.classList.add("is-visible");
    announceAssertive("Warning: Your session will expire in 2 minutes for security. Select Keep me signed in to continue.");
    const extendBtn = document.getElementById("extend-session-btn");
    if (extendBtn) extendBtn.focus();
  }

  window.extendSession = async function () {
    try {
      await apiAuthExtend();
      const bar = document.getElementById("timeout-bar");
      if (bar) bar.classList.remove("is-visible");
      sessionWarningShown = false;
      announceToScreenReader("Session extended. You are still signed in.");
    } catch (error) {
      console.error("Session extend failed:", error);
      showError("Could not extend session. Please unlock again.");
    }
  };

  function expireSession() {
    if (sessionTimerId) clearInterval(sessionTimerId);
    stopBlockchainPolling();

    const bar = document.getElementById("timeout-bar");
    if (bar) bar.classList.remove("is-visible");

    document.getElementById("auth-locked").classList.remove("hidden");
    document.getElementById("auth-unlocked").classList.add("hidden");
    document.getElementById("dashboard-section").classList.add("hidden");
    document.getElementById("grant-section").classList.add("hidden");
    document.getElementById("help-section").classList.add("hidden");

    const btn = document.getElementById("fingerprint-btn");
    if (btn) {
      btn.disabled = false;
      btn.removeAttribute("aria-busy");
    }

    state.session.active = false;
    announceAssertive("Your session has expired for security. Please unlock again to continue.");
  }

  // =========================================================================
  // BLOCKCHAIN EXPLORER LINK
  // =========================================================================

  function addBlockchainExplorerLink() {
    const footer = document.querySelector(".site-footer");
    if (!footer) return;

    const explorerLink = document.createElement("p");
    explorerLink.style.marginTop = "8px";
    explorerLink.innerHTML = `
      <a href="${CONFIG.API_BASE_URL}/blockchain/explorer" target="_blank" rel="noopener noreferrer" style="color: #FFFFFF; text-decoration: underline;">
        View Blockchain Explorer
      </a> |
      <a href="${CONFIG.API_BASE_URL}/blockchain/verify" target="_blank" rel="noopener noreferrer" style="color: #FFFFFF; text-decoration: underline;">
        Verify Chain Integrity
      </a>
    `;
    footer.appendChild(explorerLink);
  }

  // =========================================================================
  // KEYBOARD SHORTCUTS (preserve existing)
  // =========================================================================

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && state.pendingGrant) {
      cancelGrant();
    }
  });

  // =========================================================================
  // INITIALIZATION
  // =========================================================================

  document.addEventListener("DOMContentLoaded", function () {
    // Add blockchain explorer link to footer
    addBlockchainExplorerLink();

    // Set initial focus
    const skipLink = document.querySelector(".skip-link");
    if (skipLink) skipLink.focus();

    // Announce page load
    setTimeout(() => {
      announceToScreenReader("BCHAIN-ACCESS Health Records page loaded with blockchain integration. Use the skip link to jump to main content, or tab through the page.");
    }, 500);
  });

  // =========================================================================
  // EXPORTS (for module usage if needed)
  // =========================================================================

  window.BlockchainIntegration = {
    apiRequest,
    apiAuthUnlock,
    apiGetRecords,
    apiGrantAccess,
    apiConfirmAccess,
    apiCancelAccess,
    apiRevokeAccess,
    apiCheckAccess,
    apiGetAuditLog,
    apiBlockchainStatus,
    apiBlockchainExplorer,
    CONFIG,
    state,
  };
})();
