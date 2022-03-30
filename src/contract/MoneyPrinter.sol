pragma solidity ^0.5.7;
pragma experimental ABIEncoderV2;

import "./IERC20.sol";
import './IUniswapV2Router02.sol';
import './IWeth.sol';

contract MoneyPrinter  {
    address owner;

    constructor() public {
		owner = msg.sender;
    }

	modifier onlyOwner() {
		require(msg.sender == owner);
		_;
	}

	function setOwner(address _o) onlyOwner external {
		owner = _o;
	}

	function printMoney(
        address tokenIn,
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        uint256 deadline,
        address swapAddress
    ) onlyOwner public {
        IUniswapV2Router02 uni = IUniswapV2Router02(swapAddress);
        IERC20 erc20 = IERC20(tokenIn);
        erc20.transferFrom(msg.sender, address(this), amountIn);
		erc20.approve(swapAddress, amountIn); // usdt -1 six decimal would fail!
        uni.swapExactTokensForTokens(amountIn, amountOutMin, path, msg.sender, deadline);
    }

    function() external payable {}
}
