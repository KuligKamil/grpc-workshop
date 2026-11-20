# Exercise 1: Proto Messages

**Estimated time:** ~10 min

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
# From the workshop/ directory:
poe generate-exercises
# No errors → exercises/generated/ updated
```

Then run just this exercise's tests:

```bash
poe test-01
```

`poe test-exercises` runs all of them.

## ✅ Micro-check

After `poe generate-exercises` you should see **no errors** on the terminal and
these four files in `exercises/generated/`:

```
exercises/generated/chat_pb2.py
exercises/generated/chat_pb2_grpc.py
exercises/generated/chat_pb2.pyi
exercises/generated/chat_pb2_grpc.pyi
```

"No errors" only proves the file is valid syntax — the untouched `chat.proto`
with empty messages compiles too. To check that the fields are actually there,
run `poe test-01`.

Common `protoc` errors:

| `protoc` prints | What is wrong |
|---|---|
| `Missing field number.` | a field has no `= N` |
| `Field numbers must be positive integers.` | a field is numbered `= 0` |
| `Field number 1 has already been used in "Message" by field "…"` | two fields share a number |
| `Expected ";".` | a missing semicolon at the end of a field |
| `Expected field name.` | a type with no name, e.g. `string = 1;` |
| `Expected top-level statement` / `Unmatched "}"` | an extra or missing brace |

## proto3 default values

proto3 has no "field not set" for scalars: every field has a default
(`""` for strings, `0` for numbers, `false` for bools) and that default is
indistinguishable from someone explicitly sending it. The wire format simply
omits default-valued fields.

That is why `HistoryRequest.limit` is documented as *"0 = all"*: a client that
does not care about the limit sends nothing, the server reads `0`, and the
convention turns that into "no limit":

```python
limit = request.limit if request.limit > 0 else len(messages)
```

The same thing is why Exercise 3 validates `request.content`: an empty string is
what you get both from `content=""` and from omitting `content` entirely.

You can check this yourself: `HistoryRequest(room_id="x")` and
`HistoryRequest(room_id="x", limit=0)` serialize to the *same bytes*, and
`HasField("limit")` refuses to answer at all
(`Field chat.HistoryRequest.limit does not have presence`).

If you genuinely need to tell "unset" from "zero", proto3 gives you
`optional` (which adds presence tracking, so `HasField()` works) or a wrapper
message. For this workshop the `0 = all` convention is enough — but it is worth
knowing it *is* a convention, not something the protocol enforces.
