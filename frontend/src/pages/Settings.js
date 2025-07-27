import React, { useState } from 'react';
import { useUser } from '../context/UserContext';
import { 
  CurrencyDollarIcon as CurrencyRupeeIcon,
  Cog6ToothIcon,
  UserIcon,
  ChartBarIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

const Settings = () => {
  const { userSettings, updateUserSettings, saveUserSettings } = useUser();
  const [isSaving, setIsSaving] = useState(false);

  const [formData, setFormData] = useState({
    salary: userSettings.salary || 70000,
    monthlyBudget: userSettings.monthlyBudget || 100000,
    monthlyTarget: userSettings.monthlyTarget || 10000,
    riskProfile: userSettings.riskProfile || 'moderate',
    targetEqWeight: userSettings.targetEqWeight || 0.75,
    maxDrawdown: userSettings.maxDrawdown || 0.20,
    rebalThreshold: userSettings.rebalThreshold || 5,
    capitalGainsBudget: userSettings.capitalGainsBudget || 0.03,
    liquidityBufferMonths: userSettings.liquidityBufferMonths || 6,
    email: userSettings.email || 'akshay.nambiar7@gmail.com'
  });

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      updateUserSettings(formData);
      await saveUserSettings();
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const SettingSection = ({ title, icon: Icon, children }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center mb-6">
        <div className="p-2 rounded-lg bg-primary-100">
          <Icon className="h-6 w-6 text-primary-600" />
        </div>
        <h3 className="ml-3 text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {children}
    </div>
  );

  const InputField = ({ label, name, type = 'text', placeholder, min, max, step }) => (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <input
        type={type}
        name={name}
        id={name}
        value={formData[name]}
        onChange={handleInputChange}
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
      />
    </div>
  );

  const SelectField = ({ label, name, options }) => (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <select
        name={name}
        id={name}
        value={formData[name]}
        onChange={handleInputChange}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Configure your investment goals, risk profile, and portfolio preferences.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Personal Information */}
        <SettingSection title="Personal Information" icon={UserIcon}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InputField
              label="Monthly Salary (₹)"
              name="salary"
              type="number"
              placeholder="70000"
              min="0"
            />
            <InputField
              label="Email Address"
              name="email"
              type="email"
              placeholder="akshay.nambiar7@gmail.com"
            />
          </div>
        </SettingSection>

        {/* Investment Goals */}
        <SettingSection title="Investment Goals" icon={ChartBarIcon}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InputField
              label="Monthly Investment Budget (₹)"
              name="monthlyBudget"
              type="number"
              placeholder="100000"
              min="0"
            />
            <InputField
              label="Monthly Return Target (₹)"
              name="monthlyTarget"
              type="number"
              placeholder="10000"
              min="0"
            />
            <InputField
              label="Target Equity Weight (%)"
              name="targetEqWeight"
              type="number"
              placeholder="75"
              min="0"
              max="100"
              step="0.01"
            />
            <InputField
              label="Rebalancing Threshold (%)"
              name="rebalThreshold"
              type="number"
              placeholder="5"
              min="0"
              max="20"
            />
          </div>
        </SettingSection>

        {/* Risk Management */}
        <SettingSection title="Risk Management" icon={ShieldCheckIcon}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SelectField
              label="Risk Profile"
              name="riskProfile"
              options={[
                { value: 'conservative', label: 'Conservative' },
                { value: 'moderate', label: 'Moderate' },
                { value: 'aggressive', label: 'Aggressive' }
              ]}
            />
            <InputField
              label="Maximum Drawdown (%)"
              name="maxDrawdown"
              type="number"
              placeholder="20"
              min="0"
              max="50"
              step="0.01"
            />
            <InputField
              label="Capital Gains Budget (%)"
              name="capitalGainsBudget"
              type="number"
              placeholder="3"
              min="0"
              max="10"
              step="0.01"
            />
            <InputField
              label="Liquidity Buffer (months)"
              name="liquidityBufferMonths"
              type="number"
              placeholder="6"
              min="1"
              max="12"
            />
          </div>
        </SettingSection>

        {/* Summary */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Monthly Investment:</p>
              <p className="font-semibold">₹{formData.monthlyBudget?.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-gray-600">Target Return:</p>
              <p className="font-semibold">₹{formData.monthlyTarget?.toLocaleString()} ({(formData.monthlyTarget / formData.monthlyBudget * 100).toFixed(1)}%)</p>
            </div>
            <div>
              <p className="text-gray-600">Risk Profile:</p>
              <p className="font-semibold capitalize">{formData.riskProfile}</p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Saving...
              </>
            ) : (
              <>
                <Cog6ToothIcon className="h-4 w-4 mr-2" />
                Save Settings
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Settings; 