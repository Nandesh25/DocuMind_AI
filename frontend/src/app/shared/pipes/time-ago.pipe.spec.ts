import { TimeAgoPipe } from './time-ago.pipe';

describe('TimeAgoPipe', () => {
  const pipe = new TimeAgoPipe();

  it('returns empty string for null/undefined', () => {
    expect(pipe.transform(null)).toBe('');
    expect(pipe.transform(undefined)).toBe('');
  });

  it('returns "just now" for the current time', () => {
    expect(pipe.transform(new Date())).toBe('just now');
  });

  it('formats minutes (plural)', () => {
    const d = new Date(Date.now() - 5 * 60 * 1000);
    expect(pipe.transform(d)).toBe('5 minutes ago');
  });

  it('formats a single hour (singular)', () => {
    const d = new Date(Date.now() - 60 * 60 * 1000);
    expect(pipe.transform(d)).toBe('1 hour ago');
  });

  it('formats multiple hours', () => {
    const d = new Date(Date.now() - 3 * 60 * 60 * 1000);
    expect(pipe.transform(d)).toBe('3 hours ago');
  });
});
