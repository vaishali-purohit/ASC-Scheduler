/**
 * Request manager utility for handling API request optimization
 * Includes debouncing, cancellation, and timeout handling
 */

interface RequestOptions {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  signal?: AbortSignal;
  priority?: "critical" | "normal" | "low";
  enableRetry?: boolean;
  exponentialBackoff?: boolean;
}

interface PendingRequest {
  controller: AbortController;
  timeoutId: number;
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
}

class RequestManager {
  private pendingRequests = new Map<string, PendingRequest>();
  private requestCache = new Map<
    string,
    { data: unknown; timestamp: number; ttl: number }
  >();
  private readonly DEFAULT_TIMEOUT = 30000; // 30 seconds (increased from 10s)
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly REQUEST_QUEUE: Array<{
    executeFn: () => void;
    priority: "critical" | "normal" | "low";
  }> = [];
  private readonly MAX_CONCURRENT_REQUESTS = 3; // Limit concurrent requests to prevent backend overload
  private activeRequests = 0;
  private readonly DEFAULT_RETRIES = 3;
  private readonly DEFAULT_RETRY_DELAY = 1000; // 1 second

  /**
   * Check if we can execute a request (respecting concurrency limits)
   */
  private canExecuteRequest(): boolean {
    return this.activeRequests < this.MAX_CONCURRENT_REQUESTS;
  }

  /**
   * Queue a request for execution when capacity is available
   */
  private queueRequest(
    executeFn: () => void,
    priority: "critical" | "normal" | "low" = "normal"
  ): void {
    this.REQUEST_QUEUE.push({ executeFn, priority });
    // Sort queue by priority (critical first, then normal, then low)
    this.REQUEST_QUEUE.sort((a, b) => {
      const priorityOrder = { critical: 0, normal: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
    this.processQueue();
  }

  /**
   * Process the request queue
   */
  private processQueue(): void {
    while (this.canExecuteRequest() && this.REQUEST_QUEUE.length > 0) {
      const { executeFn } = this.REQUEST_QUEUE.shift()!;
      executeFn();
    }
  }

  /**
   * Mark a request as completed and process queue
   */
  private markRequestComplete(): void {
    this.activeRequests = Math.max(0, this.activeRequests - 1);
    this.processQueue();
  }

  /**
   * Calculate delay for retry with exponential backoff
   */
  private calculateRetryDelay(
    attempt: number,
    baseDelay: number,
    exponentialBackoff: boolean
  ): number {
    if (exponentialBackoff) {
      return baseDelay * Math.pow(2, attempt - 1);
    }
    return baseDelay;
  }

  /**
   * Execute request with retry logic
   */
  private async executeWithRetry<T>(
    requestFn: () => Promise<T>,
    options: RequestOptions,
    attempt: number = 1
  ): Promise<T> {
    const {
      timeout = this.DEFAULT_TIMEOUT,
      retries = this.DEFAULT_RETRIES,
      retryDelay = this.DEFAULT_RETRY_DELAY,
      exponentialBackoff = true,
      enableRetry = true,
    } = options;

    try {
      return await this.executeSingleRequest(requestFn, timeout);
    } catch (error) {
      // Don't retry on abort errors or if retries are disabled
      if (
        !enableRetry ||
        (error instanceof Error && error.name === "AbortError")
      ) {
        throw error;
      }

      // Don't retry if we've exhausted all attempts
      if (attempt >= retries) {
        throw error;
      }

      // Calculate delay and wait before retry
      const delay = this.calculateRetryDelay(
        attempt,
        retryDelay,
        exponentialBackoff
      );
      await new Promise((resolve) => setTimeout(resolve, delay));

      // Retry the request
      return this.executeWithRetry(requestFn, options, attempt + 1);
    }
  }

  /**
   * Execute a single request with timeout
   */
  private async executeSingleRequest<T>(
    requestFn: () => Promise<T>,
    timeout: number
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => {
        controller.abort();
        reject(new Error(`Request timeout after ${timeout}ms`));
      }, timeout);

      const requestPromise = requestFn();

      Promise.race([
        requestPromise,
        new Promise<never>((_, rejectTimeout) => {
          controller.signal.addEventListener("abort", () => {
            rejectTimeout(new Error(`Request timeout after ${timeout}ms`));
          });
        }),
      ])
        .then((result) => {
          window.clearTimeout(timeoutId);
          resolve(result);
        })
        .catch((error) => {
          window.clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  /**
   * Debounced request execution with queue management and retry logic
   * @param key - Unique key for the request
   * @param requestFn - Function to execute
   * @param options - Request options
   */
  async executeDebounced<T>(
    key: string,
    requestFn: () => Promise<T>,
    options: RequestOptions = {}
  ): Promise<T> {
    const { priority = "normal" } = options;

    // Check cache first
    const cached = this.getFromCache(key);
    if (cached) {
      return cached as T;
    }

    // Cancel existing pending request for this key
    this.cancelPendingRequest(key);

    return new Promise((resolve, reject) => {
      const executeRequest = async () => {
        this.activeRequests++;

        try {
          const result = await this.executeWithRetry(requestFn, options);

          // Cache successful response
          this.setCache(key, result, this.DEFAULT_TTL);

          resolve(result as T);
        } catch (error) {
          reject(error);
        } finally {
          this.markRequestComplete();
        }
      };

      // Queue or execute immediately based on capacity
      if (this.canExecuteRequest()) {
        executeRequest();
      } else {
        this.queueRequest(executeRequest, priority);
      }
    });
  }

  /**
   * Cancel a pending request
   * @param key - Request key to cancel
   */
  cancelPendingRequest(key: string): void {
    const pending = this.pendingRequests.get(key);
    if (pending) {
      pending.controller.abort();
      window.clearTimeout(pending.timeoutId);
      this.pendingRequests.delete(key);
    }
  }

  /**
   * Cancel all pending requests and clear queue
   */
  cancelAllRequests(): void {
    this.pendingRequests.forEach((_, key) => {
      this.cancelPendingRequest(key);
    });
    // Clear the request queue
    this.REQUEST_QUEUE.length = 0;
    this.activeRequests = 0;
  }

  /**
   * Set cache entry
   * @param key - Cache key
   * @param data - Data to cache
   * @param ttl - Time to live in milliseconds
   */
  private setCache(key: string, data: unknown, ttl: number): void {
    this.requestCache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });

    // Clean up old entries if cache is getting too large
    if (this.requestCache.size > 1000) {
      const entries = Array.from(this.requestCache.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      const toDelete = entries.slice(0, entries.length - 1000);
      toDelete.forEach(([key]) => this.requestCache.delete(key));
    }
  }

  /**
   * Get data from cache
   * @param key - Cache key
   * @returns Cached data or null if not found/expired
   */
  private getFromCache(key: string): unknown | null {
    const entry = this.requestCache.get(key);
    if (entry) {
      const isValid = Date.now() - entry.timestamp < entry.ttl;
      if (isValid) {
        return entry.data;
      }
      // Remove expired entry
      this.requestCache.delete(key);
    }
    return null;
  }

  /**
   * Clear all cache
   */
  clearCache(): void {
    this.requestCache.clear();
  }

  /**
   * Clear cache for specific key
   * @param key - Cache key to clear
   */
  clearCacheEntry(key: string): void {
    this.requestCache.delete(key);
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return {
      size: this.requestCache.size,
      pendingRequests: this.pendingRequests.size,
    };
  }
}

// Export singleton instance
export const requestManager = new RequestManager();

// Utility function for making debounced requests with fetch
export const makeDebouncedRequest = async <T>(
  url: string,
  options: RequestInit & RequestOptions = {}
): Promise<T> => {
  const { timeout, retries, retryDelay, signal, ...fetchOptions } = options;
  const key = `${url}:${JSON.stringify(fetchOptions)}`;

  return requestManager.executeDebounced(
    key,
    async () => {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: signal || new AbortController().signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json() as Promise<T>;
    },
    { timeout, retries, retryDelay }
  );
};
