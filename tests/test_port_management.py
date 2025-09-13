"""Test script for intelligent port management and AI proxy diagnostics"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.port_manager import SmartPortManager, AIProxyDiagnostics, EnhancedPortManager


async def test_port_management():
    """Test intelligent port management"""
    print("Testing Intelligent Port Management\n")
    
    pm = SmartPortManager()
    
    # Test port finding
    print("1. Finding free port...")
    try:
        port = pm.find_free_port(8080)
        print(f"   Found free port: {port}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test port analysis
    print("\n2. Analyzing port usage...")
    analysis = pm.analyze_port_usage(8080)
    print(f"   Port 8080 analysis: {analysis}")
    
    # Test recommendations
    print("\n3. Getting recommendations...")
    recommendations = pm.get_port_recommendations("proxy")
    print(f"   Proxy recommendations: {recommendations}")
    
    print()


async def test_ai_diagnostics():
    """Test AI proxy diagnostics (without actual proxy)"""
    print("Testing AI Proxy Diagnostics\n")
    
    ai_diag = AIProxyDiagnostics()
    
    # Test basic connectivity (will fail, but that's expected)
    print("1. Testing proxy connectivity on port 8080...")
    test_result = await ai_diag._test_basic_connectivity(8080)
    print(f"   Status: {test_result['status']}")
    print(f"   Details: {test_result['details']}")
    
    # Test quick check
    print("\n2. Quick proxy check...")
    is_healthy = await ai_diag.quick_proxy_check(8080)
    print(f"   Proxy healthy: {is_healthy}")
    
    print()


async def test_enhanced_port_manager():
    """Test enhanced port manager with AI integration"""
    print("Testing Enhanced Port Manager\n")
    
    epm = EnhancedPortManager()
    
    print("1. Setting up proxy with intelligence...")
    try:
        setup_result = await epm.setup_proxy_with_intelligence(8080)
        
        print(f"   Proxy port: {setup_result.get('proxy_port')}")
        print(f"   Success: {setup_result.get('success')}")
        
        port_selection = setup_result.get('port_selection', {})
        if port_selection.get('port_changed'):
            print(f"   Port changed from {port_selection.get('requested_port')} to {port_selection.get('assigned_port')}")
            conflict = port_selection.get('conflict_reason', {})
            if conflict:
                print(f"   Conflict reason: {conflict.get('name', 'unknown')} (PID: {conflict.get('pid', 'unknown')})")
        
        recommendations = setup_result.get('recommendations', [])
        if recommendations:
            print("   AI Recommendations:")
            for rec in recommendations[:3]:
                print(f"     - {rec}")
                
    except Exception as e:
        print(f"   Error: {e}")
    
    print()


async def main():
    """Run all tests"""
    print("Testing Intelligent Port Management & AI Proxy Diagnostics\n")
    print("=" * 70)
    
    await test_port_management()
    await test_ai_diagnostics()
    await test_enhanced_port_manager()
    
    print("All tests completed!")
    print("\nSummary:")
    print("   - Smart port conflict detection")
    print("   - AI-powered proxy diagnostics") 
    print("   - Automatic port recommendations")
    print("   - Enhanced error handling")


if __name__ == "__main__":
    asyncio.run(main())
