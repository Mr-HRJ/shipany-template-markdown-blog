import { ControllerRenderProps } from 'react-hook-form';

import { FormField } from '@/shared/types/blocks/form';

import { MdniceEditor } from '../common/mdnice-editor';

export function Markdown({
  field,
  formField,
  data,
}: {
  field: FormField;
  formField: ControllerRenderProps<Record<string, unknown>, string>;
  data?: any;
}) {
  return (
    <MdniceEditor
      value={formField.value as string}
      onChange={formField.onChange}
      placeholder={field.placeholder || ''}
      {...field.attributes}
    />
  );
}
