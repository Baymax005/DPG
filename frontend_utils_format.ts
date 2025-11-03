/**
 * DPG Frontend Utilities
 * Number formatting and display helpers
 */

/**
 * Format cryptocurrency amounts with proper precision
 * Fixes the "0.00" display issue for small amounts like 0.001 ETH
 * 
 * @param value - The numeric value to format (string or number)
 * @param decimals - Number of decimal places to show (default: 8)
 * @returns Formatted string with proper precision
 * 
 * Examples:
 *   formatCrypto("0.001") => "0.00100000"
 *   formatCrypto("0.001", 4) => "0.0010"
 *   formatCrypto("1.5") => "1.50000000"
 *   formatCrypto("1234.56789") => "1,234.56789000"
 */
export const formatCrypto = (value: string | number, decimals: number = 8): string => {
  if (!value || value === '0' || value === 0) {
    return '0.00';
  }
  
  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(num)) {
    return '0.00';
  }
  
  // For very small numbers (< 0.01), always show more decimals
  if (num < 0.01 && num > 0) {
    return num.toFixed(decimals);
  }
  
  // For numbers >= 0.01, show with thousand separators
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: decimals
  });
};

/**
 * Format fiat currency amounts
 * @param value - The numeric value
 * @param currency - Currency code (USD, EUR, etc.)
 */
export const formatFiat = (value: string | number, currency: string = 'USD'): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(num)) {
    return '$0.00';
  }
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num);
};

/**
 * Shorten blockchain address for display
 * @param address - Full address (0x...)
 * @param startChars - Characters to show at start (default: 6)
 * @param endChars - Characters to show at end (default: 4)
 */
export const shortenAddress = (
  address: string, 
  startChars: number = 6, 
  endChars: number = 4
): string => {
  if (!address || address.length < startChars + endChars) {
    return address;
  }
  
  return `${address.slice(0, startChars)}...${address.slice(-endChars)}`;
};

/**
 * Format date for transactions
 * @param date - Date string or Date object
 */
export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(d);
};

/* 
 * USAGE EXAMPLES:
 * 
 * // In your Transaction History component:
 * 
 * import { formatCrypto, formatFiat, formatDate, shortenAddress } from './utils/format';
 * 
 * <table>
 *   <tr>
 *     <td>{transaction.type}</td>
 *     <td>{formatCrypto(transaction.amount, 8)} ETH</td>
 *     <td>{formatCrypto(transaction.fee, 8)} ETH</td>
 *     <td>{transaction.status}</td>
 *     <td>{formatDate(transaction.created_at)}</td>
 *   </tr>
 * </table>
 * 
 * // In your Wallet Balance display:
 * <p>Balance: {formatCrypto(wallet.balance)} ETH</p>
 * <p>≈ {formatFiat(wallet.balance * ethPrice)}</p>
 * 
 * // For addresses:
 * <p>Address: {shortenAddress(wallet.address)}</p>
 */
