# Exercise 1: Proto Messages

## Goal

Define the remaining proto messages in `chat.proto`.
`MessageRequest` is already filled in as an example — study it, then define the rest.

## Example (already done)

```proto
message MessageRequest {
  string room_id = 1;
  string user    = 2;
  string content = 3;
}
```

## Your task

Define these four messages (field names and types are in the comments in the file):

| Message | Purpose |
|---------|---------|
| `MessageResponse` | returned after a successful `SendMessage` |
| `Message` | the stored chat message (returned by `GetHistory` / `Chat`) |
| `HistoryRequest` | request history for a room |
| `BulkResponse` | returned after a bulk upload |

## Verify

```bash
poe generate-exercises
# No errors → exercises/generated/ updated
```

## ✅ Micro-check

After `poe generate-exercises` you should see **no errors** on the terminal and
two new files in `exercises/generated/`:

```
exercises/generated/chat_pb2.py
exercises/generated/chat_pb2_grpc.py
```

If `protoc` prints `Field number 0 is illegal`, a field tag is missing.
If it prints `Expected field name`, a brace or semicolon is wrong.

## Solution

`solutions/01_protocol_buffers/chat.proto`
