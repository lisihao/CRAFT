# CRAFT - CRAFT Runs Any Framework Technology

> AI-Driven Cross-Platform API Adaptation Layer Generator

## Overview

CRAFT is an automated system that generates compatibility layers enabling applications to run across different platforms (e.g., Android to HarmonyOS). Using AI-powered code generation and semantic API mapping, CRAFT achieves massive-scale API adaptation with minimal human intervention.

## Key Features

- **AI-Driven Generation**: Leverages Claude API for intelligent code generation
- **Semantic Mapping**: Understands API semantics beyond simple signature matching
- **High Performance**: Built with Rust for memory safety and excellent performance
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
│  API Specs DB ──→  Claude AI Agent ──→  Adapter Code        │
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
├── Cargo.toml              # Workspace configuration
├── crates/
│   ├── craft-core/         # Core data structures and types
│   ├── craft-parser/       # SDK parsers (tree-sitter based)
│   ├── craft-analyzer/     # Semantic analysis engine
│   ├── craft-generator/    # Code generation (Tera templates)
│   ├── craft-ai/           # Claude API integration
│   ├── craft-pipeline/     # Batch processing pipeline
│   └── craft-cli/          # Command line interface
├── docs/                   # Design documents
├── specs/                  # API specifications (YAML)
├── templates/              # Code generation templates
├── configs/                # Configuration files
└── tools/                  # Development utilities
```

## Quick Start

### Prerequisites

- Rust 1.75+ (with cargo)
- Claude API access (Opus 4.5 recommended)
- Source platform SDK (e.g., Android SDK)
- Target platform SDK (e.g., HarmonyOS SDK)

### Installation

```bash
# Clone repository
git clone https://github.com/lisihao/CRAFT.git
cd CRAFT

# Build the project
cargo build --release

# Configure API keys
cp configs/ai_config.yaml.example configs/ai_config.yaml
# Edit ai_config.yaml with your Claude API key
```

### Basic Usage

```bash
# Parse Android SDK
craft-cli parse --platform android --sdk-path /path/to/android-sdk

# Analyze and generate mappings
craft-cli analyze --source android --target harmony

# Generate adapters for specific package
craft-cli generate --package android.app --output ./output

# Run tests
cargo test --all
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Rust | Memory safety, high performance |
| Parser | tree-sitter | High-performance code parsing |
| Async Runtime | Tokio | Asynchronous I/O operations |
| Parallelism | Rayon | CPU-bound parallel processing |
| Templates | Tera | Jinja2-compatible code generation |
| Serialization | serde | YAML/JSON configuration |
| HTTP Client | reqwest | Claude API communication |
| CLI | clap | Command line interface |

## Documentation

- [Architecture Design](docs/ARCHITECTURE_DESIGN.md) - System architecture and design decisions
- [Feasibility Analysis](docs/FEASIBILITY_ANALYSIS.md) - Technical feasibility study
- [API Bridge List](docs/TIEBA_API_BRIDGE_LIST.md) - Example API bridge analysis

## Development Status

| Phase | Status | Description |
|-------|--------|-------------|
| Foundation | In Progress | Rust infrastructure setup |
| Core Engine | Planned | Semantic mapping & generation |
| Pipeline | Planned | Automation & batch processing |
| Scale | Planned | Full API coverage |
| Production | Planned | Release-ready quality |

## Building from Source

```bash
# Debug build
cargo build

# Release build (optimized)
cargo build --release

# Run tests
cargo test --all

# Run with logging
RUST_LOG=info cargo run --bin craft-cli -- --help

# Generate documentation
cargo doc --open
```

## Contributing

We welcome contributions! Please see our contributing guidelines.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Android Open Source Project (AOSP)
- OpenHarmony Project
- Anthropic Claude for AI capabilities
- Rust community for excellent tooling

---

*Built with AI-assisted development using Claude Code*
