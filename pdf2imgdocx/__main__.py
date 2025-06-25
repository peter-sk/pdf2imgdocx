import click
from multiprocessing import cpu_count

from .core import pdf_to_word_appendix

@click.command()
@click.argument('pdf_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('word_output', type=click.Path(dir_okay=False))
@click.option('--temp-dir', default='temp_pages', show_default=True,
              help='Temporary directory for intermediate files')
@click.option('--dpi', default=300, show_default=True, type=int,
              help='Resolution in DPI for PDF to image conversion')
@click.option('--width', default=8.27, show_default=True, type=float,
              help='Width in inches for image insertion in Word')
@click.option('--height', default=11.69, show_default=True, type=float,
              help='Height in inches (A4 default) for image insertion in Word')
@click.option('--num-proc', default=cpu_count(), show_default=True, type=int,
              help='Number of parallel processes for image conversion')
@click.option('--cleanup/--no-cleanup', default=True, show_default=True,
              help='Remove temporary files after processing')
def main(pdf_path, word_output, temp_dir, dpi, width, height, num_proc, cleanup):
    """
    CLI wrapper for PDF to Word conversion.
    """
    click.echo(f"Reading PDF: {pdf_path}")
    click.echo(f"Converting using {num_proc} processes at {dpi} DPI...")
    pdf_to_word_appendix(
        pdf_path=pdf_path,
        word_output=word_output,
        temp_dir=temp_dir,
        dpi=dpi,
        width=width,
        height=height,
        num_proc=num_proc,
        cleanup=cleanup,
    )
    click.echo(f"Saved Word document to: {word_output}")
    click.echo("Done.")

if __name__ == '__main__':
    main()
