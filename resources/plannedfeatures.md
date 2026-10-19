# Planned Features

This document describes planned ideas for Symul Browser. These are plans, not claims that the features are already implemented.

## 1. Universal Command Bar

### Overview

Remap `Ctrl+T` to open a compact visual command popup instead of immediately creating a blank tab. The popup should appear with its input field already focused, so the user can start typing immediately.

The input acts as a combined address bar, web search box, and command launcher. Symul interprets the input and routes it to the appropriate action.

### Input behaviour

- **URL or domain:** navigate to the entered address in a new tab.
- **Ordinary search text:** search Google in a new tab.
- **Slash command:** execute the matching command, passing along the remaining text as its argument.
- **Tab or agent query:** find relevant open tabs or monitored AI agents and allow the user to switch to them.
- **Empty input:** show useful suggestions, available commands, recent items, or quick actions.

Examples:

| Input | Intended action |
| --- | --- |
| `chatgpt.com` | Open ChatGPT in a new tab |
| `weather Sydney` | Search Google for the query |
| `/ai hi there` | Send `hi there` to the configured AI destination |
| `/tabs` | Find and manage open tabs |
| `/agents` | View monitored AI agents |
| `/help` | Show available commands |

The command list should be extensible. Commands can be handled by separate modules so adding a command does not require rewriting the command bar.

### Interaction and UI

- Use a visual popup styled consistently with Symul's dark interface.
- Focus the input automatically when the popup opens.
- Support keyboard navigation, Enter to activate the selected item, and Escape to close the popup.
- Show relevant suggestions as the user types.
- Keep the interface lightweight and responsive; simple actions such as switching tabs should not require an AI model or network request.
- Preserve a way to explicitly create a normal new tab from the popup.

### AI routing

The `/ai` command should send its remaining text to a configured AI destination. The design may later support explicit provider selection, such as `/ai claude ...` or `/ai gpt ...`, as well as a configurable default provider. Provider-specific behaviour should be isolated behind handlers rather than embedded into the command bar itself.

## 2. Search Tab Consolidation and Memory Use

### Overview

Create a browser feature, potentially implemented using Symul's extension system, that reduces the clutter and memory cost of opening many Google search tabs.

The initial concept is to combine or manage multiple Google search tabs through a single search workspace. Users should still be able to revisit previous queries and their results without keeping every search page independently active.

### Goals

- Detect relevant Google search tabs.
- Provide one organised workspace for multiple searches.
- Preserve access to previous queries and results.
- Avoid unnecessarily opening duplicate search pages where possible.
- Restore or revisit a search when requested.

### Memory considerations

Combining tabs visually does not by itself reduce memory use if all original pages remain loaded. Meaningful memory savings require reducing duplicate page loads and/or suspending or unloading inactive pages, then restoring them when needed. Any implementation should preserve a sensible way to return to a suspended search and should not silently discard the user's work.

The precise workspace UI and suspension strategy remain to be designed.

## 3. AI Agent Monitor and Quick Switcher

### Overview

Provide a central view of browser tabs running AI agents, such as Claude, so users can see what each agent appears to be doing and quickly switch to the relevant tab.

The initial scope is **monitoring and navigation, not remote control**. Symul does not need to automate clicks or send instructions into third-party AI websites to provide the core value.

### Status detection

A monitoring component can observe relevant page DOM changes, for example with `MutationObserver`, and inspect supported status indicators or text. Depending on the site, useful signals may include:

- The agent is generating or working.
- The task appears to have completed.
- The agent is waiting for user input or approval.
- An error or interruption is shown.

Status detection will need to be adapted to the websites being supported. DOM structure and wording can change, and a quiet page does not necessarily mean a task is finished. Where the state cannot be determined reliably, show an **Unknown** state rather than guessing.

### Agent overview

The command popup or a dedicated view should list detected agents with useful context, such as:

- Agent or website name.
- Task or page title, where available.
- Best-effort status: Working, Completed, Waiting, or Unknown.
- A quick action to focus the corresponding tab.

Status indicators should be informative without claiming more certainty than the page provides.

### Unified quick switching

Make it fast to move between monitored agents and ordinary browser tabs from the same command interface. Searching for an agent or tab should bring up a selectable result, and activating it should focus the existing tab rather than opening a duplicate.

Future versions may extend switching to other work tools, but the initial feature should focus on browser tabs and web-based AI agents.

### Scope boundary

The agent monitor is not intended to become a remote page-action automation framework. Sending prompts, clicking approval buttons, and controlling agent workflows are outside the initial scope. The priority is visibility, status awareness, and quick navigation.

## Suggested Architecture

Keep the features modular and connect them through a small browser-level interface:

- **Command bar:** popup UI, input interpretation, suggestions, keyboard handling, and command dispatch.
- **Command handlers:** URL navigation, Google search, AI routing, tab search, and other slash commands.
- **Search workspace:** search-tab discovery, query organisation, and any future page suspension/restoration logic.
- **Agent monitor:** site-specific DOM/status detection and normalised agent status.
- **Tab switcher:** shared search and navigation across regular tabs and monitored agents.

This separation should allow each feature to evolve independently while sharing the command bar as the common entry point.

## Development Principles

- Keep the command bar fast and keyboard-friendly.
- Make ordinary browser actions work without an AI dependency.
- Prefer explicit, understandable routing over surprising guesses.
- Treat website DOM monitoring as best-effort and resilient to unknown states.
- Do not equate tab consolidation with memory savings unless inactive pages are actually prevented from loading or suspended.
- Clearly distinguish planned functionality from implemented functionality.
