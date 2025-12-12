#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

cd website
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"
npm run build
ls -la .next/
