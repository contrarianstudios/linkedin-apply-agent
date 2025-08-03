// Working LinkedIn MCP Web Client Example
// This handles the MCP protocol correctly for web apps

class LinkedInMCPClient {
    constructor() {
        this.baseURL = 'http://localhost:8000/mcp';
        this.sessionId = null;
    }

    async initialize() {
        try {
            const response = await fetch(this.baseURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/event-stream'
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "initialize",
                    params: {
                        protocolVersion: "2024-11-05",
                        capabilities: {},
                        clientInfo: {
                            name: "web-client",
                            version: "1.0.0"
                        }
                    },
                    id: 1
                })
            });

            // Extract session ID from headers
            this.sessionId = response.headers.get('mcp-session-id');
            console.log('Session ID:', this.sessionId);
            
            return response.ok;
        } catch (error) {
            console.error('Initialize failed:', error);
            return false;
        }
    }

    async callTool(toolName, args = {}) {
        if (!this.sessionId) {
            throw new Error('Not initialized - call initialize() first');
        }

        try {
            const response = await fetch(this.baseURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/event-stream',
                    'X-MCP-Session-ID': this.sessionId
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "tools/call",
                    params: {
                        name: toolName,
                        arguments: args
                    },
                    id: Date.now()
                })
            });

            return await response.json();
        } catch (error) {
            console.error(`Tool ${toolName} failed:`, error);
            throw error;
        }
    }

    // Convenient methods for LinkedIn tools
    async searchJobs(searchTerm) {
        return this.callTool('search_jobs', { search_term: searchTerm });
    }

    async getPersonProfile(username) {
        return this.callTool('get_person_profile', { linkedin_username: username });
    }

    async getCompanyProfile(companyName) {
        return this.callTool('get_company_profile', { company_name: companyName });
    }

    async getRecommendedJobs() {
        return this.callTool('get_recommended_jobs');
    }
}

// Usage Example:
async function testLinkedInMCP() {
    const client = new LinkedInMCPClient();
    
    // Initialize connection
    const initialized = await client.initialize();
    if (!initialized) {
        console.error('Failed to initialize');
        return;
    }

    try {
        // Search for jobs
        console.log('Searching for jobs...');
        const jobs = await client.searchJobs('software engineer');
        console.log('Jobs found:', jobs);

        // Get a profile
        console.log('Getting profile...');
        const profile = await client.getPersonProfile('stickerdaniel');
        console.log('Profile:', profile);

    } catch (error) {
        console.error('Test failed:', error);
    }
}

// Export for use in web apps
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LinkedInMCPClient;
}

// Auto-run test if in browser console
if (typeof window !== 'undefined') {
    window.LinkedInMCPClient = LinkedInMCPClient;
    window.testLinkedInMCP = testLinkedInMCP;
    console.log('LinkedIn MCP Client loaded! Try: testLinkedInMCP()');
} 