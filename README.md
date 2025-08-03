# LinkedIn Apply Agent

A powerful LinkedIn automation and data extraction tool built with MCP (Model Context Protocol) integration for seamless AI assistant connectivity.

## 🚀 Features

- **LinkedIn Job Search** - Automated job searching with filters
- **Profile Data Extraction** - Detailed LinkedIn profile information  
- **Company Intelligence** - Comprehensive company research
- **MCP Integration** - Direct integration with Claude and other AI assistants
- **Web API** - HTTP server for web application integration
- **Multi-Client Support** - Python, JavaScript, and web interfaces

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Chrome browser
- [uv](https://github.com/astral-sh/uv) package manager

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/contrarianstudios/linkedin-apply-agent.git
cd linkedin-apply-agent

# Install dependencies
uv sync

# Install ChromeDriver (macOS)
curl -o chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.184/mac-arm64/chromedriver-mac-arm64.zip"
unzip chromedriver.zip
sudo mv chromedriver-mac-arm64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

## 🔑 Authentication

### Get LinkedIn Cookie

**Option 1: Automated (Recommended)**
```bash
uv run main.py --get-cookie
```

**Option 2: Manual**
1. Login to LinkedIn in your browser
2. Open DevTools (F12) → Application → Cookies → linkedin.com
3. Copy the `li_at` cookie value
4. Set as environment variable: `export LINKEDIN_COOKIE="your_cookie_here"`

## 🖥️ Usage

### Claude Desktop Integration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "uv",
      "args": [
        "--directory", 
        "/path/to/linkedin-apply-agent", 
        "run", 
        "main.py"
      ],
      "env": {
        "LINKEDIN_COOKIE": "your_linkedin_cookie_here"
      }
    }
  }
}
```

### HTTP Server Mode

```bash
# Start HTTP server
LINKEDIN_COOKIE="your_cookie" uv run main.py --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp

# Server available at: http://localhost:8000/mcp
```

### Python Client

```python
from fixed_mcp_client import ProperMCPClient

client = ProperMCPClient("http://localhost:8000/mcp")
client.initialize()

# Search for jobs
jobs = client.call_tool('search_jobs', {'search_term': 'software engineer'})

# Get profile
profile = client.call_tool('get_person_profile', {'linkedin_username': 'johndoe'})
```

### JavaScript/Web Integration

```javascript
import LinkedInMCPClient from './working_web_example.js';

const client = new LinkedInMCPClient();
await client.initialize();

const jobs = await client.searchJobs('python developer');
const profile = await client.getPersonProfile('username');
```

## 🔧 Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_jobs` | Search LinkedIn jobs | `search_term` |
| `get_person_profile` | Get LinkedIn profile | `linkedin_username` |
| `get_company_profile` | Get company information | `company_name`, `get_employees` |
| `get_job_details` | Get specific job details | `job_id` |
| `get_recommended_jobs` | Get personalized job recommendations | none |
| `close_session` | Clean up browser session | none |

## 📊 Example Responses

### Job Search
```json
{
  "result": [
    {
      "job_title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA (Remote)",
      "linkedin_url": "https://linkedin.com/jobs/view/123456789",
      "posted_date": "2024-01-15",
      "applicant_count": "50-100"
    }
  ]
}
```

### Profile Data
```json
{
  "result": {
    "name": "John Doe",
    "headline": "Senior Software Engineer at Tech Corp",
    "location": "San Francisco Bay Area",
    "experience": [...],
    "education": [...],
    "skills": [...]
  }
}
```

## 🌐 Web Integration

See `web-integration-guide.md` for comprehensive web application integration examples including:

- Next.js/React components
- Express.js backend integration
- Vanilla JavaScript clients
- Complete API documentation

## 🧪 Testing

```bash
# Test the HTTP server
uv run python fixed_mcp_client.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector
# Then connect to: http://localhost:8000/mcp
```

## 📁 Project Structure

```
linkedin-apply-agent/
├── linkedin_mcp_server/          # Core MCP server implementation
├── fixed_mcp_client.py          # Working Python client
├── working_web_example.js       # JavaScript client implementation  
├── web-integration-guide.md     # Comprehensive integration guide
├── web-test.html                # Browser testing interface
└── main.py                      # Server entry point
```

## ⚠️ Important Notes

- **Rate Limiting**: Respect LinkedIn's servers - avoid excessive requests
- **Cookie Expiration**: LinkedIn cookies expire ~30 days, refresh as needed
- **Terms of Service**: Use responsibly and in accordance with LinkedIn's ToS
- **Privacy**: Server runs locally, your data stays private

## 🐛 Troubleshooting

### Common Issues

**"Missing session ID" Error**
- Ensure you're using the complete MCP protocol handshake
- Check that `notifications/initialized` is sent after initialize

**Chrome Driver Issues**
- Verify Chrome and ChromeDriver versions match
- Check ChromeDriver is in PATH or set `CHROMEDRIVER_PATH`

**LinkedIn Authentication Failed**
- Refresh your LinkedIn cookie
- Try logging out and back into LinkedIn
- Use `--no-headless` flag to debug visually

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## 🔗 Links

- **Repository**: https://github.com/contrarianstudios/linkedin-apply-agent
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Claude Desktop**: https://claude.ai/download

---

⭐ **Star this repo if it helps you automate your LinkedIn workflow!**


<br/>
<br/>


## Acknowledgements
Built with [LinkedIn Scraper](https://github.com/joeyism/linkedin_scraper) by [@joeyism](https://github.com/joeyism) and [FastMCP](https://gofastmcp.com/).

⚠️ Use in accordance with [LinkedIn's Terms of Service](https://www.linkedin.com/legal/user-agreement). Web scraping may violate LinkedIn's terms. This tool is for personal use only.

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=stickerdaniel/linkedin-mcp-server&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=stickerdaniel/linkedin-mcp-server&type=Date" />
  <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=stickerdaniel/linkedin-mcp-server&type=Date" />
</picture>


## License

This project is licensed under the Apache 2.0 license.

<br>
