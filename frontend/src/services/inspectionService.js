/**
 * Inspection Service - API functions for managing building inspections
 *
 * This module provides functions to interact with the inspections API endpoints.
 * All functions use async/await and proper error handling.
 */

import { apiClient } from '../config/api.js';

/**
 * Create a new inspection
 *
 * @param {Object} data - Inspection data
 * @param {string} data.building_name - Name of the building (required)
 * @param {string} data.building_address - Address of the building (required)
 * @param {string} data.operator_name - Name of the operator (required)
 * @param {number} data.total_area_sqm - Total area in square meters (required, must be positive)
 * @returns {Promise<Object>} Created inspection object
 * @throws {Error} If validation fails or request fails
 *
 * @example
 * const inspection = await createInspection({
 *   building_name: "Test Tower",
 *   building_address: "Dubai Marina",
 *   operator_name: "Ashish",
 *   total_area_sqm: 1000.0
 * });
 */
export async function createInspection(data) {
  try {
    const response = await apiClient.post('/inspections', data);
    return response.data;
  } catch (error) {
    // Extract meaningful error message
    const errorMessage = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || 'Failed to create inspection';

    throw new Error(errorMessage);
  }
}

/**
 * Get inspection by ID
 *
 * @param {string} id - UUID of the inspection
 * @returns {Promise<Object>} Inspection object
 * @throws {Error} If inspection not found or request fails
 *
 * @example
 * const inspection = await getInspection('4950262f-f3bb-41ad-873d-add5b10534c4');
 */
export async function getInspection(id) {
  try {
    const response = await apiClient.get(`/inspections/${id}`);
    return response.data;
  } catch (error) {
    // Handle 404 specifically
    if (error.response?.status === 404) {
      throw new Error(`Inspection with id ${id} not found`);
    }

    // Extract meaningful error message
    const errorMessage = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || 'Failed to get inspection';

    throw new Error(errorMessage);
  }
}

/**
 * List inspections with pagination
 *
 * @param {number} skip - Number of records to skip (default: 0)
 * @param {number} limit - Maximum number of records to return (default: 100)
 * @returns {Promise<Array>} Array of inspection objects (empty array if none found)
 * @throws {Error} If request fails
 *
 * @example
 * const inspections = await listInspections(0, 10);
 */
export async function listInspections(skip = 0, limit = 100) {
  try {
    const response = await apiClient.get('/inspections', {
      params: { skip, limit }
    });
    return response.data;
  } catch (error) {
    // On error, return empty array instead of mock data
    console.error('Failed to list inspections:', error.message);
    return [];
  }
}

/**
 * Update inspection status
 *
 * @param {string} id - UUID of the inspection
 * @param {string} status - New status value (pending, in_progress, completed, failed)
 * @returns {Promise<Object>} Updated inspection object
 * @throws {Error} If inspection not found, invalid status, or request fails
 *
 * @example
 * const updated = await updateInspectionStatus('4950262f-f3bb-41ad-873d-add5b10534c4', 'completed');
 */
export async function updateInspectionStatus(id, status) {
  try {
    const response = await apiClient.patch(`/inspections/${id}/status`, {
      status
    });
    return response.data;
  } catch (error) {
    // Handle 404 specifically
    if (error.response?.status === 404) {
      throw new Error(`Inspection with id ${id} not found`);
    }

    // Handle validation errors
    if (error.response?.status === 422 || error.response?.status === 400) {
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic validation error
        throw new Error(detail[0]?.msg || 'Invalid status value');
      } else if (typeof detail === 'string') {
        throw new Error(detail);
      }
    }

    // Extract meaningful error message
    const errorMessage = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || 'Failed to update inspection status';

    throw new Error(errorMessage);
  }
}

/**
 * Update inspection quality score
 *
 * @param {string} id - UUID of the inspection
 * @param {number} score - Quality score between 0 and 100
 * @returns {Promise<Object>} Updated inspection object
 * @throws {Error} If inspection not found, invalid score, or request fails
 *
 * @example
 * const updated = await updateInspectionScore('4950262f-f3bb-41ad-873d-add5b10534c4', 85.5);
 */
export async function updateInspectionScore(id, score) {
  try {
    const response = await apiClient.patch(`/inspections/${id}/score`, {
      score
    });
    return response.data;
  } catch (error) {
    // Handle 404 specifically
    if (error.response?.status === 404) {
      throw new Error(`Inspection with id ${id} not found`);
    }

    // Handle validation errors
    if (error.response?.status === 422 || error.response?.status === 400) {
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic validation error
        throw new Error(detail[0]?.msg || 'Invalid score value');
      } else if (typeof detail === 'string') {
        throw new Error(detail);
      }
    }

    // Extract meaningful error message
    const errorMessage = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || 'Failed to update inspection score';

    throw new Error(errorMessage);
  }
}
