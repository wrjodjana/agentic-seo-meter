for p in python3 python py; do
  if "$p" -c 'import sys; sys.exit(sys.version_info < (3,))' >/dev/null 2>&1; then
    exec "$p" "$@"
  fi
done
echo "agentic-seo-meter: Python 3 was not found on PATH" >&2
exit 1
