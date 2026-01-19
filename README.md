# CRAFT - CRAFT Runs Any Framework Technology

> AI-Driven Cross-Platform API Adaptation Layer Generator

## Overview

CRAFT is an automated system that generates compatibility layers enabling applications to run across different platforms (e.g., Android to HarmonyOS). Using AI-powered code generation and semantic API mapping, CRAFT achieves massive-scale API adaptation with minimal human intervention.

## Key Features

- **AI-Driven Generation**: Leverages Claude Code for intelligent code generation
- **Semantic Mapping**: Understands API semantics beyond simple signature matching
- **Automated Testing**: Auto-generates comprehensive test suites for all adapters
- **Incremental Updates**: Efficiently handles SDK version updates
- **High Coverage**: Targets 90%+ API coverage across frameworks

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CRAFT Pipeline                            │
│                                                              │
│  Source SDK  ──→  API Analyzer  ──→  Semantic Mapper        │
│       │                                      │               │
│       ▼                                      ▼               │
│  API Specs DB ──→  Claude Code Agent ──→  Adapter Code      │
│       │                                      │               │
│       ▼                                      ▼               │
│  Target SDK ──→  Test Generator  ──→  Quality Gate          │
│                                              │               │
│                                              ▼               │
│                                       Shim Library          │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
CRAFT/
├── docs/                    # Design documents
├── src/
│   ├── core/               # Core data structures
│   ├── analyzers/          # SDK parsers & analyzers
│   ├── generators/         # Code generators
│   ├── testing/            # Test framework
│   └── pipeline/           # Automation pipeline
├── specs/                  # API specifications
├── templates/              # Code templates
├── configs/                # Configuration files
└── tools/                  # Development utilities
```

## Quick Start

### Prerequisites

- Python 3.11+
- Claude API access (Opus 4.5 recommended)
- Source platform SDK (e.g., Android SDK)
- Target platform SDK (e.g., HarmonyOS SDK)

### Installation

```bash
# Clone repository
git clone https://github.com/lisihao/CRAFT.git
cd CRAFT

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp configs/ai_config.yaml.example configs/ai_config.yaml
# Edit ai_config.yaml with your Claude API key
```

### Basic Usage

```bash
# Parse Android SDK
python -m craft.tools.sdk_parser --sdk android --path /path/to/android-sdk

# Generate adapters for specific package
python -m craft.pipeline.generate --package android.app

# Run tests
python -m pytest src/testing/
```

## Documentation

- [Architecture Design](docs/ARCHITECTURE_DESIGN.md) - System architecture and design decisions
- [Feasibility Analysis](docs/FEASIBILITY_ANALYSIS.md) - Technical feasibility study
- [API Bridge List](docs/TIEBA_API_BRIDGE_LIST.md) - Example API bridge analysis

## Development Status

| Phase | Status | Description |
|-------|--------|-------------|
| Foundation | In Progress | Basic infrastructure setup |
| Core Engine | Planned | Semantic mapping & generation |
| Pipeline | Planned | Automation & batch processing |
| Scale | Planned | Full API coverage |
| Production | Planned | Release-ready quality |

## Contributing

We welcome contributions! Please see our contributing guidelines.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Android Open Source Project (AOSP)
- OpenHarmony Project
- Anthropic Claude for AI capabilities

---

*Built with AI-assisted development using Claude Code*
