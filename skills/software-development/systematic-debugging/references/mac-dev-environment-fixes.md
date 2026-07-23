# macOS Dev Environment Fixes

Quick-reference fixes for recurring macOS development environment issues.
Each entry follows the systematic-debugging pattern: symptom → root cause → fix → verification.

## pyenv: cannot rehash — lock file stuck

**Symptom:** `pyenv: cannot rehash: couldn't acquire lock ~/.pyenv/shims/.pyenv-shim for 60 seconds`
**Root cause:** pyenv uses `noclobber` on `~/.pyenv/shims/.pyenv-shim` as an atomic lock. If a previous `pyenv rehash` was killed (Ctrl+C, crash, OOM), the file remains — blocking all future rehash attempts.
**Diagnosis:**
```bash
# Check if the file exists (it's both the prototype shim AND the lock)
ls -la ~/.pyenv/shims/.pyenv-shim
# No processes holding it? It's stale
lsof ~/.pyenv/shims/.pyenv-shim
```
**Fix:**
```bash
rm -f ~/.pyenv/shims/.pyenv-shim
pyenv rehash
```
**Verification:** Open a new terminal — the error should be gone.

## zsh startup: pyenv init slow

**Symptom:** New zsh terminal takes 2-5 seconds to appear.
**Root cause:** `pyenv init` in `.zshrc` runs `pyenv rehash` on every shell startup.
**Diagnosis:**
```bash
# Time pyenv init
time pyenv init > /dev/null
```
**Fix (if slow):** Consider lazy-loading pyenv in `.zshrc`:
```bash
# Only init pyenv when first called, not on every shell spawn
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
# Skip pyenv init for non-interactive shells
if [[ -o interactive ]]; then
  eval "$(pyenv init -)"
fi
```
