const { spawn } = require('child_process');
const fs = require('fs');

// Function to run agent-browser command
function runAgentBrowser(args) {
  return new Promise((resolve, reject) => {
    const headers = '{"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}';
    const child = spawn('agent-browser', args, {
      env: { ...process.env, AGENT_BROWSER_HEADERS: headers }
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(`Command failed with code ${code}: ${stderr}`));
      }
    });
  });
}

// Function to extract holdings from the snapshot
function extractHoldings(snapshot) {
  // Find the holdings section in the snapshot
  const holdingsSectionStart = snapshot.indexOf('10 大持股 (佔總資產');
  if (holdingsSectionStart === -1) {
    throw new Error('Could not find holdings section');
  }

  // Extract the relevant part of the snapshot
  const relevantPart = snapshot.substring(holdingsSectionStart);

  // Regular expression to match stock codes and percentages
  // Looking for patterns like "stock_code text percentage%"
  const holdingRegex = /([A-Z0-9]+\.[A-Z]+)\s+([\d.]+%)|([A-Z0-9]+)\s+([\d.]+%)/g;
  
  const holdings = [];
  let match;
  while ((match = holdingRegex.exec(relevantPart)) !== null) {
    let stockCode, percentage;
    
    if (match[1] && match[2]) {
      // Matched format: "stock_code percentage%"
      stockCode = match[1];
      percentage = parseFloat(match[2].replace('%', ''));
    } else if (match[3] && match[4]) {
      // Matched format: "stock_code percentage%" (without dot)
      stockCode = match[3];
      percentage = parseFloat(match[4].replace('%', ''));
    }
    
    if (stockCode && !isNaN(percentage)) {
      holdings.push({ stockCode, percentage });
      
      // Only get top 10
      if (holdings.length >= 10) {
        break;
      }
    }
  }

  return holdings;
}

// Function to extract PE ratio from a stock page snapshot
async function extractPeRatio(stockCode) {
  try {
    // Navigate to the stock page
    await runAgentBrowser(['open', `https://hk.finance.yahoo.com/quote/${stockCode}/`]);
    
    // Get snapshot of the stock page
    const snapshot = await runAgentBrowser(['snapshot']);
    
    // Look for PE ratio in the snapshot
    // Common patterns for PE ratio on Yahoo Finance
    const pePatterns = [
      /市盈率 \(最近 12 個月\)\s+([\d.]+)/,
      /Trailing P\/E\s+([\d.]+)/,
      /PE Ratio \(TTM\)\s+([\d.]+)/,
      /Price-to-Earnings Ratio\s+([\d.]+)/
    ];
    
    for (const pattern of pePatterns) {
      const match = snapshot.match(pattern);
      if (match) {
        return parseFloat(match[1]);
      }
    }
    
    console.log(`Could not find PE ratio for ${stockCode}`);
    return null;
  } catch (error) {
    console.error(`Error getting PE ratio for ${stockCode}:`, error.message);
    return null;
  }
}

// Main function
async function main() {
  try {
    console.log('Fetching KWEB holdings...');
    
    // Open KWEB page
    await runAgentBrowser(['open', 'https://hk.finance.yahoo.com/quote/KWEB/']);
    
    // Get snapshot of the page
    const snapshot = await runAgentBrowser(['snapshot']);
    
    // Extract holdings
    const holdings = extractHoldings(snapshot);
    
    console.log('Top 10 Holdings:');
    holdings.forEach((holding, index) => {
      console.log(`${index + 1}. ${holding.stockCode}: ${holding.percentage}%`);
    });
    
    // Calculate total percentage of top 10 holdings
    const top10Percentage = holdings.reduce((sum, holding) => sum + holding.percentage, 0);
    console.log(`\nTotal percentage of top 10 holdings: ${top10Percentage}%`);
    
    // Calculate remaining percentage
    const remainingPercentage = 100 - top10Percentage;
    console.log(`Remaining percentage (other holdings): ${remainingPercentage}%`);
    
    // Get PE ratios for each holding
    console.log('\nFetching PE ratios for each holding...');
    const peRatios = [];
    
    for (const holding of holdings) {
      console.log(`Getting PE ratio for ${holding.stockCode}...`);
      const peRatio = await extractPeRatio(holding.stockCode);
      peRatios.push({
        stockCode: holding.stockCode,
        percentage: holding.percentage,
        peRatio: peRatio
      });
      
      // Log the result
      if (peRatio !== null) {
        console.log(`  PE ratio for ${holding.stockCode}: ${peRatio}`);
      } else {
        console.log(`  Could not find PE ratio for ${holding.stockCode}`);
      }
    }
    
    // Calculate weighted PE ratio
    // For stocks where we couldn't find the PE ratio, we'll assume 20
    // For the remaining holdings, we'll also assume 20
    let weightedSum = 0;
    let totalPercentageUsed = 0;
    
    for (const holding of peRatios) {
      const peRatio = holding.peRatio !== null ? holding.peRatio : 20;
      weightedSum += (holding.percentage / 100) * peRatio;
      totalPercentageUsed += holding.percentage;
    }
    
    // Add contribution from remaining holdings (assumed PE = 20)
    weightedSum += (remainingPercentage / 100) * 20;
    totalPercentageUsed += remainingPercentage;
    
    const weightedPERatio = weightedSum;
    
    console.log('\nWeighted PE Ratio Calculation:');
    console.log('-----------------------------');
    peRatios.forEach(holding => {
      const peRatio = holding.peRatio !== null ? holding.peRatio : 20;
      console.log(`${holding.stockCode}: ${holding.percentage}% * ${peRatio} = ${(holding.percentage/100 * peRatio).toFixed(4)}`);
    });
    console.log(`Other holdings: ${remainingPercentage}% * 20 = ${(remainingPercentage/100 * 20).toFixed(4)}`);
    console.log(`\nTotal weighted PE ratio: ${weightedPERatio.toFixed(4)}`);
    
    // Save results to a file
    const results = {
      holdings: peRatios,
      remainingPercentage,
      weightedPERatio,
      timestamp: new Date().toISOString()
    };
    
    fs.writeFileSync('kweb_pe_analysis.json', JSON.stringify(results, null, 2));
    console.log('\nResults saved to kweb_pe_analysis.json');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run the main function
main();