/**
 * ProgramFilter
 *
 * Lightweight text input used to filter feedback by program/event/product
 * name. Shares the toolbar styling with the search input.
 */
import { useEffect, useState } from "react";

export default function ProgramFilter({
  value = "",
  onChange,
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
    <input
      type="text"
      className="form__control"
      style={{ maxWidth: 240 }}
      placeholder="Filter by program..."
      value={internal}
      onChange={(e) => setInternal(e.target.value)}
      aria-label="Filter by program"
    />
  );
}
