# Rust Starter Template

A minimal Rust starter project for quickly bootstrapping new applications. Opinionated but lightweight, focused on fast setup, consistent tooling, and clean structure.

## Features

- Clean project layout with sensible defaults
- Built-in formatting and linting (rustfmt + clippy)
- Ready-to-run dev workflow (`cargo run`, `cargo test`)
- Example config pattern and environment loading hook

## Getting Started

- Rust toolchain (stable) via rustup
- Cargo (bundled with Rust)
- Rust Syntax (vscode plugin)
- rust-analyzer (vscode plugin)
- rustfmt (vscode plugin)
- clippy (vscode plugin)

### Shell

```bash
cargo run
```

```bash
cargo test
```

```bash
cargo publish
```

```bash
cargo add {crates}
```

```bash
cargo remove {crates}
```

```bash
cargo update {crates}
```

### Lint and Format

```bash
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
```

## License

MIT. See `LICENSE` for details.

## Contributing

Issues and PRs are welcome, but every change needs a reason to convince me. If it's just a feature request, I won't accept it because this is my template. You can fork one for your own use
