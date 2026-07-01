import { FileSizePipe } from './file-size.pipe';

describe('FileSizePipe', () => {
  const pipe = new FileSizePipe();

  it('returns "0 B" for zero, null, or undefined', () => {
    expect(pipe.transform(0)).toBe('0 B');
    expect(pipe.transform(null)).toBe('0 B');
    expect(pipe.transform(undefined)).toBe('0 B');
  });

  it('formats bytes without decimals', () => {
    expect(pipe.transform(512)).toBe('512 B');
  });

  it('formats kilobytes with one decimal', () => {
    expect(pipe.transform(1536)).toBe('1.5 KB');
  });

  it('drops decimals for values >= 10', () => {
    expect(pipe.transform(10 * 1024 * 1024)).toBe('10 MB');
  });
});
