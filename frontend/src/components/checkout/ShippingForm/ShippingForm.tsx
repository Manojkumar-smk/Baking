import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { ShippingAddress } from '@/types/order.types'
import styles from './ShippingForm.module.css'

const shippingSchema = z.object({
  full_name: z.string().min(1, 'Full name is required'),
  street_address: z.string().min(1, 'Street address is required'),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(1, 'State is required'),
  postal_code: z.string().min(1, 'Postal code is required'),
  country: z.string().min(1, 'Country is required'),
  phone: z.string().optional(),
})

type ShippingFormData = z.infer<typeof shippingSchema>

interface ShippingFormProps {
  initialData?: Partial<ShippingAddress>
  onSubmit: (data: ShippingAddress) => void
  onBack?: () => void
}

const ShippingForm = ({ initialData, onSubmit, onBack }: ShippingFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ShippingFormData>({
    resolver: zodResolver(shippingSchema),
    defaultValues: {
      full_name: initialData?.full_name || '',
      street_address: initialData?.street_address || '',
      city: initialData?.city || '',
      state: initialData?.state || '',
      postal_code: initialData?.postal_code || '',
      country: initialData?.country || 'US',
      phone: initialData?.phone || '',
    },
  })

  const handleFormSubmit = (data: ShippingFormData) => {
    onSubmit(data as ShippingAddress)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className={styles.form}>
      <h2 className={styles.title}>Shipping Address</h2>

      <div className={styles.formGroup}>
        <label htmlFor="full_name" className={styles.label}>
          Full Name *
        </label>
        <input
          type="text"
          id="full_name"
          {...register('full_name')}
          className={errors.full_name ? styles.inputError : styles.input}
        />
        {errors.full_name && (
          <span className={styles.error}>{errors.full_name.message}</span>
        )}
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="street_address" className={styles.label}>
          Street Address *
        </label>
        <input
          type="text"
          id="street_address"
          {...register('street_address')}
          className={errors.street_address ? styles.inputError : styles.input}
        />
        {errors.street_address && (
          <span className={styles.error}>{errors.street_address.message}</span>
        )}
      </div>

      <div className={styles.formRow}>
        <div className={styles.formGroup}>
          <label htmlFor="city" className={styles.label}>
            City *
          </label>
          <input
            type="text"
            id="city"
            {...register('city')}
            className={errors.city ? styles.inputError : styles.input}
          />
          {errors.city && (
            <span className={styles.error}>{errors.city.message}</span>
          )}
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="state" className={styles.label}>
            State *
          </label>
          <input
            type="text"
            id="state"
            {...register('state')}
            className={errors.state ? styles.inputError : styles.input}
          />
          {errors.state && (
            <span className={styles.error}>{errors.state.message}</span>
          )}
        </div>
      </div>

      <div className={styles.formRow}>
        <div className={styles.formGroup}>
          <label htmlFor="postal_code" className={styles.label}>
            Postal Code *
          </label>
          <input
            type="text"
            id="postal_code"
            {...register('postal_code')}
            className={errors.postal_code ? styles.inputError : styles.input}
          />
          {errors.postal_code && (
            <span className={styles.error}>{errors.postal_code.message}</span>
          )}
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="country" className={styles.label}>
            Country *
          </label>
          <select
            id="country"
            {...register('country')}
            className={errors.country ? styles.inputError : styles.input}
          >
            <option value="US">United States</option>
            <option value="CA">Canada</option>
            <option value="GB">United Kingdom</option>
            <option value="AU">Australia</option>
          </select>
          {errors.country && (
            <span className={styles.error}>{errors.country.message}</span>
          )}
        </div>
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="phone" className={styles.label}>
          Phone Number (Optional)
        </label>
        <input
          type="tel"
          id="phone"
          {...register('phone')}
          className={errors.phone ? styles.inputError : styles.input}
        />
        {errors.phone && (
          <span className={styles.error}>{errors.phone.message}</span>
        )}
      </div>

      <div className={styles.actions}>
        {onBack && (
          <button type="button" onClick={onBack} className={styles.backBtn}>
            Back to Cart
          </button>
        )}
        <button type="submit" disabled={isSubmitting} className={styles.submitBtn}>
          {isSubmitting ? 'Processing...' : 'Continue to Payment'}
        </button>
      </div>
    </form>
  )
}

export default ShippingForm
