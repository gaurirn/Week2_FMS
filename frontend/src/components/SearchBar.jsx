/**
 * SearchBar
 *
 * Controlled search input with a small debounce so typing doesn't
 * trigger an HTTP request per keystroke.
 */
import { useEffect, useState } from "react";

export default function SearchBar({
  value = "",
  onChange,
  placeholder = "Search by name, program or keyword...",
  delay = 350,
}) {
  const [internal, setInternal] = useState(value);

  useEffect(() => {
    setInternal(value);
  }, [value]);

  useEffect(() => {
    const handle = setTimeout(() => {
      if (internal !== value) onChange?.(internal);
    }, delay);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [internal]);

  return (
    <div className="toolbar__search">
      <input
        type="search"
        className="form__control"
        placeholder={placeholder}
        value={internal}
        onChange={(e) => setInternal(e.target.value)}
        aria-label="Search feedback"
      />
    </div>
  );
}
