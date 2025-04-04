# Receipt AI

npm run [timestamp] [id] [merchant_name] [amount] [currency] [folder_to_dump]

uv run main.py

## Resources

https://github.com/gumloop/guMCP/tree/main/src/servers/gmail

Getting the credentials: https://github.com/gumloop/GuMCP/blob/main/src/servers/gmail/README.md

Using the inspector: https://github.com/modelcontextprotocol/inspector

uv add "mcp[cli]"


## Run locally
### Env.example
```txt
ANTHROPIC_API_KEY=example_str
CREDS_FILE_PATH=example_str
TOKEN_JSON_PATH=example._str
```

### Cmd
`make dev`


### run
Trigger
- Download transaction from brex -step
- Identify transactions without receipts -step
- Call tool to search for receipts (linear) {id; loc;}
- Upload transaction receipts
