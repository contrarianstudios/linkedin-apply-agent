# LinkedIn MCP Server - Web Integration Guide

## Overview
The LinkedIn MCP server can be integrated into web-based Claude applications in several ways:

## Option 1: HTTP MCP Server (Recommended)

### Start the Server
```bash
LINKEDIN_COOKIE="your_cookie_here" uv run main.py \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8000 \
  --path /mcp \
  --log-level INFO
```

### API Endpoints
- **Base URL**: `http://127.0.0.1:8000/mcp`
- **Method**: POST
- **Content-Type**: `application/json`

### Example API Calls

#### List Available Tools
```javascript
const response = await fetch('http://127.0.0.1:8000/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: "2.0",
    method: "tools/list",
    params: {},
    id: 1
  })
});
const tools = await response.json();
```

#### Search Jobs
```javascript
const searchJobs = async (searchTerm) => {
  const response = await fetch('http://127.0.0.1:8000/mcp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "tools/call",
      params: {
        name: "search_jobs",
        arguments: { search_term: searchTerm }
      },
      id: 2
    })
  });
  return await response.json();
};
```

#### Get Person Profile
```javascript
const getProfile = async (username) => {
  const response = await fetch('http://127.0.0.1:8000/mcp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "tools/call",
      params: {
        name: "get_person_profile",
        arguments: { linkedin_username: username }
      },
      id: 3
    })
  });
  return await response.json();
};
```

## Option 2: Claude API Integration

### Frontend Integration with Claude API
```javascript
class LinkedInClaudeAgent {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.mcpServerUrl = 'http://127.0.0.1:8000/mcp';
  }

  async queryLinkedInWithClaude(userPrompt) {
    // First, get available LinkedIn tools
    const tools = await this.getLinkedInTools();
    
    // Send to Claude API with tool definitions
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 1024,
        tools: tools.result.tools,
        messages: [{
          role: 'user',
          content: userPrompt
        }]
      })
    });

    const result = await response.json();
    
    // If Claude wants to use a tool, execute it via MCP
    if (result.stop_reason === 'tool_use') {
      const toolCall = result.content.find(c => c.type === 'tool_use');
      const toolResult = await this.executeLinkedInTool(
        toolCall.name, 
        toolCall.input
      );
      
      // Send tool result back to Claude for final response
      // ... continuation logic
    }
    
    return result;
  }

  async getLinkedInTools() {
    const response = await fetch(this.mcpServerUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "tools/list",
        params: {},
        id: 1
      })
    });
    return await response.json();
  }

  async executeLinkedInTool(toolName, toolArgs) {
    const response = await fetch(this.mcpServerUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "tools/call",
        params: {
          name: toolName,
          arguments: toolArgs
        },
        id: Date.now()
      })
    });
    return await response.json();
  }
}
```

### Usage Example
```javascript
const agent = new LinkedInClaudeAgent('your-claude-api-key');

// Example queries
const result1 = await agent.queryLinkedInWithClaude(
  "Find software engineer jobs in San Francisco"
);

const result2 = await agent.queryLinkedInWithClaude(
  "Research the profile of LinkedIn user 'stickerdaniel'"
);

const result3 = await agent.queryLinkedInWithClaude(
  "Get information about Anthropic's company page on LinkedIn"
);
```

## Option 3: Next.js/React Integration

### API Route (`pages/api/linkedin.js`)
```javascript
export default async function handler(req, res) {
  const { method, tool, args } = req.body;

  try {
    const response = await fetch('http://127.0.0.1:8000/mcp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: method,
        params: tool ? { name: tool, arguments: args } : {},
        id: Date.now()
      })
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

### React Component
```jsx
import { useState } from 'react';

export default function LinkedInSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);

  const searchJobs = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/linkedin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: 'tools/call',
          tool: 'search_jobs',
          args: { search_term: searchTerm }
        })
      });
      
      const data = await response.json();
      setJobs(data.result.content[0].structuredContent.result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search for jobs..."
      />
      <button onClick={searchJobs} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      
      <div>
        {jobs.map((job, index) => (
          <div key={index}>
            <h3>{job.job_title}</h3>
            <p>{job.company} - {job.location}</p>
            <a href={job.linkedin_url} target="_blank">View Job</a>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Option 4: Express.js Backend Integration

```javascript
const express = require('express');
const fetch = require('node-fetch');

const app = express();
app.use(express.json());

// LinkedIn MCP proxy endpoint
app.post('/api/linkedin/:tool', async (req, res) => {
  try {
    const { tool } = req.params;
    const args = req.body;

    const response = await fetch('http://127.0.0.1:8000/mcp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "tools/call",
        params: { name: tool, arguments: args },
        id: Date.now()
      })
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Example usage endpoints
app.get('/jobs/:searchTerm', async (req, res) => {
  const response = await fetch('http://localhost:3000/api/linkedin/search_jobs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ search_term: req.params.searchTerm })
  });
  
  const data = await response.json();
  res.json(data);
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Available LinkedIn Tools

1. **get_person_profile** - Get LinkedIn profile data
   - Args: `{ linkedin_username: "username" }`

2. **get_company_profile** - Get company information  
   - Args: `{ company_name: "company", get_employees: false }`

3. **get_job_details** - Get specific job details
   - Args: `{ job_id: "job_id" }`

4. **search_jobs** - Search for jobs
   - Args: `{ search_term: "search_term" }`

5. **get_recommended_jobs** - Get personalized recommendations
   - Args: `{}`

6. **close_session** - Clean up browser session
   - Args: `{}`

## Security Considerations

1. **CORS**: Configure CORS properly for frontend access
2. **Authentication**: Secure your LinkedIn cookie
3. **Rate Limiting**: Implement rate limiting to avoid LinkedIn blocks
4. **Environment Variables**: Store sensitive data in env vars
5. **HTTPS**: Use HTTPS in production

## Example Environment Setup

```bash
# .env file
LINKEDIN_COOKIE=your_linkedin_cookie_here
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
CLAUDE_API_KEY=your_claude_api_key
```

This setup allows you to build powerful LinkedIn-integrated web applications with Claude's AI capabilities! 