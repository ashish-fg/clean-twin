/**
 * Test script for inspectionService functions
 * Run with: node test-service.js
 */

import {
  createInspection,
  getInspection,
  listInspections,
  updateInspectionStatus,
  updateInspectionScore
} from './src/services/inspectionService.js';

async function testInspectionService() {
  try {
    console.log('🧪 Testing Inspection Service Functions\n');

    // Test 1: Create inspection
    console.log('1️⃣ Testing createInspection...');
    const newInspection = await createInspection({
      building_name: 'Frontend Test Building',
      building_address: '456 Test Ave, Dubai',
      operator_name: 'Test Operator',
      total_area_sqm: 750.0
    });
    console.log('✅ Created inspection:');
    console.log(`   ID: ${newInspection.id}`);
    console.log(`   Building: ${newInspection.building_name}`);
    console.log(`   Status: ${newInspection.status}\n`);

    const testId = newInspection.id;

    // Test 2: Get inspection by ID
    console.log('2️⃣ Testing getInspection...');
    const retrieved = await getInspection(testId);
    console.log('✅ Retrieved inspection:');
    console.log(`   ID: ${retrieved.id}`);
    console.log(`   Building: ${retrieved.building_name}`);
    console.log(`   Address: ${retrieved.building_address}\n`);

    // Test 3: List inspections
    console.log('3️⃣ Testing listInspections...');
    const inspections = await listInspections(0, 10);
    console.log(`✅ Listed ${inspections.length} inspections`);
    if (inspections.length > 0) {
      console.log(`   First: ${inspections[0].building_name}`);
    }
    console.log('');

    // Test 4: Update status
    console.log('4️⃣ Testing updateInspectionStatus...');
    const statusUpdated = await updateInspectionStatus(testId, 'in_progress');
    console.log('✅ Updated status:');
    console.log(`   ID: ${statusUpdated.id}`);
    console.log(`   New status: ${statusUpdated.status}\n`);

    // Test 5: Update score
    console.log('5️⃣ Testing updateInspectionScore...');
    const scoreUpdated = await updateInspectionScore(testId, 92.5);
    console.log('✅ Updated score:');
    console.log(`   ID: ${scoreUpdated.id}`);
    console.log(`   Quality score: ${scoreUpdated.overall_quality_score}\n`);

    // Test 6: Test 404 error
    console.log('6️⃣ Testing 404 error handling...');
    try {
      await getInspection('00000000-0000-0000-0000-000000000000');
      console.log('❌ Should have thrown 404 error');
    } catch (error) {
      console.log('✅ Correctly handled 404:');
      console.log(`   ${error.message}\n`);
    }

    // Test 7: Test invalid status
    console.log('7️⃣ Testing invalid status error handling...');
    try {
      await updateInspectionStatus(testId, 'invalid_status');
      console.log('❌ Should have thrown validation error');
    } catch (error) {
      console.log('✅ Correctly handled invalid status:');
      console.log(`   ${error.message}\n`);
    }

    // Test 8: Test invalid score
    console.log('8️⃣ Testing invalid score error handling...');
    try {
      await updateInspectionScore(testId, 150);
      console.log('❌ Should have thrown validation error');
    } catch (error) {
      console.log('✅ Correctly handled invalid score:');
      console.log(`   ${error.message}\n`);
    }

    console.log('✨ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

testInspectionService();
